import requests
from datetime import datetime

# --- CONFIGURATION DES CLÉS ---
ODDS_API_KEY = "d914452a154bb6476d95f243508d2591"
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"  # Évite les doublons et met à jour la cote
}

# Les 5 grands championnats avec les bonnes clés de l'API v4
CHAMPIONNATS = {
    "soccer_epl": "Premier League",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_spain_la_liga": "La Liga",
    "soccer_italy_serie_a": "Serie A",
    "soccer_germany_bundesliga": "Bundesliga"
}

date_du_jour = datetime.now().strftime('%Y-%m-%d')
print(f"=== COMPARATEUR DU TOP DES BOOKMAKERS FR ({date_du_jour}) ===")

# --- ÉTAPE 1 : Récupérer les matchs et équipes depuis Supabase ---
res_matchs = requests.get(
    f"{SUPABASE_URL}/rest/v1/match?date_match=gte.{date_du_jour}",
    headers=HEADERS_SUPA
)
matchs_bdd = res_matchs.json()

if not matchs_bdd:
    print(" Aucun match à venir trouvé dans Supabase. Exécute d'abord le script de tes matchs !")
else:
    print(f" {len(matchs_bdd)} matchs récupérés depuis Supabase. Analyse des cotes...")

    # Chargement des équipes pour pouvoir associer les IDs de ta BDD aux cotes
    res_equipes = requests.get(
        f"{SUPABASE_URL}/rest/v1/equipe",
        headers=HEADERS_SUPA
    )
    equipes = {e["id_equipe"]: e["nom_equipe"] for e in res_equipes.json()}

    liste_cotes_finales = []

    # --- ÉTAPE 2 : Analyse des cotes championnat par championnat ---
    for sport_key, nom_champi in CHAMPIONNATS.items():
        response = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
        )

        if response.status_code != 200:
            print(f"   Erreur sur le championnat {nom_champi} (Code {response.status_code})")
            continue

        matchs_odds = response.json()

        for match_odd in matchs_odds:
            equipe_dom_api = match_odd["home_team"]
            equipe_ext_api = match_odd["away_team"]
            date_match_api = match_odd["commence_time"][:10]

            # Recherche intelligente du match correspondant dans Supabase
            id_match = None
            for m in matchs_bdd:
                if m["date_match"] == date_match_api:
                    nom_dom_bdd = equipes.get(m["id_equipe_dom"], "")
                    nom_ext_bdd = equipes.get(m["id_equipe_ext"], "")

                    # Vérification souple pour contourner les écarts d'écriture ("FC", tirets, etc.)
                    if (equipe_dom_api in nom_dom_bdd or nom_dom_bdd in equipe_dom_api) or \
                       (equipe_dom_api.split()[0] == nom_dom_bdd.split()[0]):
                        if (equipe_ext_api in nom_ext_bdd or nom_ext_bdd in equipe_ext_api) or \
                           (equipe_ext_api.split()[0] == nom_ext_bdd.split()[0]):
                            id_match = m["id_match"]
                            break

            # Si le match n'est pas dans ta BDD, on passe au suivant
            if not id_match:
                continue

            # Initialisation des meilleures cotes pour ce match
            best_1, bookie_1 = 0.0, ""
            best_n, bookie_n = 0.0, ""
            best_2, bookie_2 = 0.0, ""

            # On parcourt les bookmakers renvoyés par l'API
            for bookie in match_odd["bookmakers"]:
                key_bookie = bookie["key"].lower()
                
                # --- FILTRE SOUPLE ET INTELLIGENT ---
                # On valide si la clé contient un opérateur agréé en France
                est_un_bookie_fr = False
                if "winamax" in key_bookie:
                    est_un_bookie_fr = True
                elif "betclic" in key_bookie:
                    est_un_bookie_fr = True
                elif "pmu" in key_bookie:
                    est_un_bookie_fr = True
                elif "unibet" in key_bookie:
                    # On évite les déclinaisons étrangères (UK, NL, SE, IT...)
                    if not any(pays in key_bookie for pays in ["_uk", "_nl", "_se", "_it", "_au", "_us"]):
                        est_un_bookie_fr = True

                # Si le bookmaker n'est pas validé comme FR, on l'ignore
                if not est_un_bookie_fr:
                    continue

                for market in bookie["markets"]:
                    if market["key"] != "h2h":
                        continue

                    for outcome in market["outcomes"]:
                        price = float(outcome["price"])
                        name = outcome["name"]

                        # Filtre comparatif : On garde uniquement la cote maximale
                        if name == equipe_dom_api and price > best_1:
                            best_1 = price
                            bookie_1 = bookie["title"]
                        elif name == "Draw" and price > best_n:
                            best_n = price
                            bookie_n = bookie["title"]
                        elif name == equipe_ext_api and price > best_2:
                            best_2 = price
                            bookie_2 = bookie["title"]

            # Si le script a extrait des cotes valides
            if best_1 > 0:
                liste_cotes_finales.append({
                    "id_match": id_match,
                    "cote_1": best_1,
                    "bookmaker_1": bookie_1,
                    "cote_n": best_n,
                    "bookmaker_n": bookie_n,
                    "cote_2": best_2,
                    "bookmaker_2": bookie_2
                })

                print(f"\n {equipe_dom_api} vs {equipe_ext_api} ({nom_champi})")
                print(f"    Meilleur 1 : {best_1} chez {bookie_1}")
                print(f"    Meilleur N : {best_n} chez {bookie_n}")
                print(f"    Meilleur 2 : {best_2} chez {bookie_2}")

    # --- ÉTAPE 3 : Insertion groupée dans Supabase ---
    if liste_cotes_finales:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/cote",
            headers=HEADERS_SUPA,
            json=liste_cotes_finales
        )

        if res.status_code in [200, 201, 204]:
            print(f"\n[BDD]  Réussite ! {len(liste_cotes_finales)} lignes de cotes insérées ou mises à jour.")
        else:
            print(f"\n[BDD] Erreur lors de l'envoi : {res.text}")
    else:
        print("\n Aucune cote exploitable trouvée pour les critères français.")

print("\n=== FIN DE LA SYNCHRONISATION ===")