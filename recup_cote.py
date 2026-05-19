import requests
from datetime import datetime

# --- CONFIGURATION DES CLÉS ---
ODDS_API_KEY = "d914452a154bb6476d95f243508d2591" #API DE the odds API
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

CHAMPIONNATS = {
    "soccer_epl": "Premier League",
    "soccer_spain_la_liga": "La Liga",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_italy_serie_a": "Serie A",
    "soccer_germany_bundesliga": "Bundesliga"
}

# Mapping de secours pour les chaînes de texte
DICTIONNAIRE_MAPPING = {
    "Tottenham Hotspur": "Tottenham Hotspur FC",
    "Athletic Bilbao": "Athletic Club",
    "Atletico Madrid": "Atlético de Madrid",
    "Real Sociedad": "Real Sociedad de Fútbol",
    "Espanyol": "RCD Espanyol de Barcelona",
    "Inter Milan": "FC Internazionale Milano"
}

def nettoyer_nom(nom):
    if not nom or not isinstance(nom, str):
        return ""
    nom = nom.lower().strip()
    parasites = [
        "fc", "cf", "afc", "rc", "as", "ssc", "ac", "us", "ud", "ca", "the", "club", 
        "stade", "olympique", "de", "di", "san", "saint", "fútbol", "futbol", "rcd"
    ]
    mots = nom.replace("-", " ").split()
    mots_filtres = [m for m in mots if m not in parasites]
    return " ".join(mots_filtres).strip()

def correspondent(nom_api, nom_bdd):
    if nom_api in DICTIONNAIRE_MAPPING:
        if DICTIONNAIRE_MAPPING[nom_api] == nom_bdd:
            return True

    api_clean = nettoyer_nom(nom_api)
    bdd_clean = nettoyer_nom(nom_bdd)
    
    if not api_clean or not bdd_clean:
        return False
        
    if (api_clean == bdd_clean) or (api_clean in bdd_clean) or (bdd_clean in api_clean):
        return True
        
    mots_api = api_clean.split()
    mots_bdd = bdd_clean.split()
    if mots_api and mots_bdd and (mots_api[0] == mots_bdd[0]):
        return True
        
    return False

date_du_jour = datetime.now().strftime('%Y-%m-%d')
print(f"--- DÉBUT DE SYNCHRONISATION ({date_du_jour}) ---")

# 1. JOINTURE DIRECTE : On demande à Supabase d'inclure les noms des équipes
# ATTENTION : Si tes colonnes de liaison s'appellent id_equipe_dom et id_equipe_ext, Supabase fait la jointure tout seul avec la syntaxe ci-dessous
url_jointure = f"{SUPABASE_URL}/rest/v1/match?select=id_match,date_match,id_equipe_dom(nom_equipe),id_equipe_ext(nom_equipe)&date_match=gte.{date_du_jour}"
res_matchs = requests.get(url_jointure, headers=HEADERS_SUPA)
matchs_bdd = res_matchs.json()

if not isinstance(matchs_bdd, list):
    print("❌ Erreur de structure Supabase ou colonnes de clés étrangères mal nommées.")
    print(matchs_bdd)
    exit()

print(f"[BDD] {len(matchs_bdd)} matchs à venir récupérés.")

dictionnaire_cotes_uniques = {}

# 2. Interrogation de l'API
for sport_key, nom_champi in CHAMPIONNATS.items():
    response = requests.get(
        f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/",
        params={"apiKey": ODDS_API_KEY, "regions": "fr", "markets": "h2h", "oddsFormat": "decimal"}
    )

    if response.status_code != 200:
        continue

    matchs_odds = response.json()

    for match_odd in matchs_odds:
        dom_api = match_odd["home_team"]
        ext_api = match_odd["away_team"]
        date_api = match_odd["commence_time"][:10]
        
        id_match_bdd = None

        for m in matchs_bdd:
            # Extraction des noms d'équipes récupérés via la jointure Supabase
            try:
                nom_dom_bdd = m["id_equipe_dom"]["nom_equipe"]
                nom_ext_bdd = m["id_equipe_ext"]["nom_equipe"]
            except (TypeError, KeyError):
                # Si la jointure échoue parce que le nom de la table est différent, on passe
                continue

            date_bdd = m["date_match"]

            # Tolérance de 5 jours pour caler l'API et ta BDD
            if abs((datetime.strptime(date_api, '%Y-%m-%d') - datetime.strptime(date_bdd, '%Y-%m-%d')).days) <= 5:
                if correspondent(dom_api, nom_dom_bdd) and correspondent(ext_api, nom_ext_bdd):
                    id_match_bdd = m["id_match"]
                    break

        if not id_match_bdd:
            continue

        # Extraction des meilleures cotes
        best_1, bookie_1 = 0.0, ""
        best_n, bookie_n = 0.0, ""
        best_2, bookie_2 = 0.0, ""

        for bookie in match_odd["bookmakers"]:
            for market in bookie['markets']:
                if market['key'] == "h2h":
                    for outcome in market['outcomes']:
                        price = float(outcome['price'])
                        name = outcome['name']

                        if correspondent(name, dom_api) and price > best_1:
                            best_1 = price
                            bookie_1 = bookie['title']
                        elif name == "Draw" and price > best_n:
                            best_n = price
                            bookie_n = bookie['title']
                        elif correspondent(name, ext_api) and price > best_2:
                            best_2 = price
                            bookie_2 = bookie['title']

        if best_1 > 0:
            dictionnaire_cotes_uniques[id_match_bdd] = {
                "id_match": id_match_bdd,
                "cote_1": best_1,
                "bookmaker_1": bookie_1,
                "cote_n": best_n,
                "bookmaker_n": bookie_n,
                "cote_2": best_2,
                "bookmaker_2": bookie_2
            }
            print(f"  MATCH ASSOCIÉ : {dom_api} vs {ext_api} -> ID BDD: {id_match_bdd}")

# 3. Envoi vers la table 'cote'
liste_cotes_finales = list(dictionnaire_cotes_uniques.values())
if liste_cotes_finales:
    url_upsert = f"{SUPABASE_URL}/rest/v1/cote?on_conflict=id_match"
    res = requests.post(url_upsert, headers=HEADERS_SUPA, json=liste_cotes_finales)
    print(f"\n[SUPABASE] Statut : {res.status_code}. {len(liste_cotes_finales)} cotes synchronisées !")
else:
    print("\nAucune correspondance trouvée.")