import requests
from bs4 import BeautifulSoup
from datetime import datetime

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

CHAMPIONNATS_TM = {
    39: "https://www.transfermarkt.fr/premier-league/verletztespieler/wettbewerb/GB1",
    61: "https://www.transfermarkt.fr/ligue-1/verletztespieler/wettbewerb/FR1",
    140: "https://www.transfermarkt.fr/laliga/verletztespieler/wettbewerb/ES1",
    135: "https://www.transfermarkt.fr/serie-a/verletztespieler/wettbewerb/IT1",
    78: "https://www.transfermarkt.fr/bundesliga/verletztespieler/wettbewerb/L1"
}

headers_tm = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

aujourd_hui = datetime.now()
date_du_jour = aujourd_hui.strftime('%Y-%m-%d')

print(f"--- Matchs du {date_du_jour} ---")

# --- ÉTAPE 1 : Récupérer les matchs depuis Supabase ---
res = requests.get(
    f"{SUPABASE_URL}/rest/v1/match?date_match=eq.{date_du_jour}",
    headers=HEADERS_SUPA
)
matchs = res.json()

if not matchs:
    print("Pas de matchs aujourd'hui dans Supabase")
else:
    print(f"{len(matchs)} matchs trouvés dans Supabase")

    # On récupère les IDs des équipes qui jouent aujourd'hui
    ids_equipes = set()
    for match in matchs:
        ids_equipes.add(match["id_equipe_dom"])
        ids_equipes.add(match["id_equipe_ext"])

    # On récupère les noms des équipes depuis Supabase
    equipes_du_jour = {}
    for id_equipe in ids_equipes:
        res_eq = requests.get(
            f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{id_equipe}",
            headers=HEADERS_SUPA
        )
        equipe = res_eq.json()
        if equipe:
            equipes_du_jour[equipe[0]["nom_equipe"]] = id_equipe

    # --- ÉTAPE 2 : Scrapper les absents sur Transfermarkt ---
    absents_par_equipe = {}

    for league_id, url_tm in CHAMPIONNATS_TM.items():
        response_tm = requests.get(url_tm, headers=headers_tm)
        soup = BeautifulSoup(response_tm.text, 'html.parser')
        lignes = soup.find_all("tr", class_=["odd", "even"])

        for ligne in lignes:
            nom_td = ligne.find("td", class_="hauptlink")
            if not nom_td:
                continue
            nom = nom_td.text.strip()

            logo_club = ligne.find("img", class_="tiny_wappen")
            club = logo_club["alt"] if logo_club else "Inconnu"

            if club in equipes_du_jour:
                if club not in absents_par_equipe:
                    absents_par_equipe[club] = []
                absents_par_equipe[club].append(nom)

    # --- ÉTAPE 3 : Insertion des joueurs absents dans la BDD ---
    print("\n--- ENVOI DES NOUVEAUX JOUEURS ABSENTS ---")
    for match in matchs:
        res_dom = requests.get(f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{match['id_equipe_dom']}", headers=HEADERS_SUPA).json()
        res_ext = requests.get(f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{match['id_equipe_ext']}", headers=HEADERS_SUPA).json()

        dom = res_dom[0]["nom_equipe"] if res_dom else "Inconnu"
        ext = res_ext[0]["nom_equipe"] if res_ext else "Inconnu"

        infos_match_equipes = [
            {"nom": dom, "id": match['id_equipe_dom']},
            {"nom": ext, "id": match['id_equipe_ext']}
        ]

        for eq in infos_match_equipes:
            if eq["nom"] == "Inconnu":
                continue
                
            absents = absents_par_equipe.get(eq["nom"], [])
            if absents:
                for joueur in absents:
                    # Payload ajusté exactement selon ton image :
                    # 'nom' prend la valeur complète, 'prenom' reste vide, 'id_equipe' et 'absent' sont fournis
                    payload = {
                        "nom": joueur,
                        "prenom": "",
                        "id_equipe": eq["id"],
                        "absent": True
                    }
                    
                    url_insert = f"{SUPABASE_URL}/rest/v1/joueur"
                    res_insert = requests.post(url_insert, headers=HEADERS_SUPA, json=payload)
                    
                    if res_insert.status_code in [200, 201, 204]:
                        print(f"   {joueur} ({eq['nom']}) inséré dans la table joueur.")
                    else:
                        print(f"   Erreur d'insertion pour {joueur}: {res_insert.status_code}")
            else:
                print(f"  Aucun absent à ajouter pour {eq['nom']}")