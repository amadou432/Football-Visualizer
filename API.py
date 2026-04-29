import requests
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "da751d251758c34be7716e2e5383976f" # Ta clé qui marche !
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates" 
}

date_du_jour = datetime.now().strftime('%Y-%m-%d')
print(f"---  Début de la synchro mondiale pour : {date_du_jour} ---")

# --- 1. RÉCUPÉRATION ---
url_api = "https://v3.football.api-sports.io/fixtures"
response = requests.get(
    url_api,
    headers={"x-apisports-key": API_KEY},
    params={"date": date_du_jour}
)

data = response.json()
matchs_api = data.get("response", [])

if not matchs_api:
    print(" Aucun match trouvé sur l'API aujourd'hui.")
else:
    print(f" {len(matchs_api)} matchs récupérés. Préparation de l'envoi...")

    equipes_dict = {}
    liste_matchs = []

    # --- 2. TRAITEMENT ---
    for match in matchs_api:
        heure_match = match["fixture"]["date"][11:16]

        # Gestion des équipes
        for side in ["home", "away"]:
            team = match["teams"][side]
            equipes_dict[team["id"]] = {
                "id_equipe": team["id"],
                "nom_equipe": team["name"],
                "logo_equipe": team["logo"]
            }

        # Gestion des matchs
        liste_matchs.append({
            "id_match": match["fixture"]["id"],
            "date_match": match["fixture"]["date"][:10],
            "heure": heure_match,
            "nom_champi": match["league"]["name"],
            "id_equipe_dom": match["teams"]["home"]["id"],
            "id_equipe_ext": match["teams"]["away"]["id"],
        })

    liste_equipes_final = list(equipes_dict.values())

    # --- 3. ENVOI À SUPABASE ---
    print(f" Envoi en cours vers Supabase...")
    
    # Envoi des équipes
    requests.post(f"{SUPABASE_URL}/rest/v1/equipe", headers=HEADERS_SUPA, json=liste_equipes_final)
    
    # Envoi des matchs
    res = requests.post(f"{SUPABASE_URL}/rest/v1/match", headers=HEADERS_SUPA, json=liste_matchs)

    if res.status_code in [200, 201, 204]:
        print(f" RÉUSSITE TOTALE ! {len(liste_matchs)} matchs sont maintenant dans ta base.")
    else:
        print(f" Erreur lors de l'envoi : {res.text}")

print("--- Fin du script ---")