import requests
import time
 
# ============================================================
# CONFIGURATION FOOTBALL-DATA.ORG
# ============================================================
API_KEY = "cd1427ada30b4ce08d0b447f29938e76"
BASE_URL = "https://api.football-data.org/v4"
 
HEADERS_FD = {
    "X-Auth-Token": API_KEY
}
 
CHAMPIONNATS = {
    "Premier League": "PL",
    "Ligue 1":        "FL1",
    "La Liga":        "PD",
    "Serie A":        "SA",
    "Bundesliga":     "BL1",
}
 
# ============================================================
# CONFIGURATION SUPABASE
# ============================================================
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"
 
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}
 
# ============================================================
# FONCTIONS
# ============================================================
 
def get_equipes_championnat(code_championnat):
    url = f"{BASE_URL}/competitions/{code_championnat}/teams?season=2025"
    response = requests.get(url, headers=HEADERS_FD)
    if response.status_code != 200:
        print(f"Erreur {response.status_code} : {response.json().get('message', '')}")
        return []
    return response.json().get("teams", [])
 
 
def insert_joueurs(joueurs):
    if not joueurs:
        return
    requests.post(
        f"{SUPABASE_URL}/rest/v1/joueur",
        headers=HEADERS_SUPA,
        json=joueurs
    )
 
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print("=== RECUPERATION JOUEURS FOOTBALL-DATA.ORG (saison 2025-2026) ===\n")
 
total_joueurs = 0
 
for nom_champi, code in CHAMPIONNATS.items():
    print(f"\n--- {nom_champi} ---")
    equipes = get_equipes_championnat(code)
    print(f"{len(equipes)} equipes trouvees")
 
    for equipe in equipes:
        nom_equipe = equipe.get("name", "")
        joueurs_api = equipe.get("squad", [])
        print(f"  {nom_equipe} — {len(joueurs_api)} joueurs")
 
        joueurs_a_inserer = []
        for joueur in joueurs_api:
            joueurs_a_inserer.append({
                "nom_joueur": joueur.get("name", ""),
                "poste":      joueur.get("position", "Inconnu"),
                "nom_equipe": nom_equipe,
            })
 
        insert_joueurs(joueurs_a_inserer)
        total_joueurs += len(joueurs_a_inserer)
        time.sleep(0.3)
 
print(f"\n=== FIN — {total_joueurs} joueurs enregistres au total ===")