import requests
import time
import random
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"
 
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
 
CHAMPIONNATS_SOFA = {
    "Premier League": {"tournament_id": 17,  "season_id": 76986},
    "Ligue 1":        {"tournament_id": 34,  "season_id": 77356},
    "La Liga":        {"tournament_id": 8,   "season_id": 77559},
    "Serie A":        {"tournament_id": 23,  "season_id": 76457},
    "Bundesliga":     {"tournament_id": 35,  "season_id": 77333},
}
 
def creer_driver():
    """Crée un navigateur Chrome qui ressemble à un humain"""
    options = Options()
    options.add_argument("--headless")  # invisible à l'écran
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--window-size=1920,1080")
 
    driver = webdriver.Chrome(options=options)
    # Masque le fait qu'on utilise Selenium
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver
 
def fetch_json(driver, url):
    """Utilise Selenium pour récupérer du JSON depuis Sofascore"""
    driver.get(url)
    time.sleep(random.uniform(2, 4))  # délai humain
    try:
        body = driver.find_element("tag name", "body").text
        return json.loads(body)
    except:
        return {}
 
def get_matchs_termines(driver, tournament_id, season_id):
    """Récupère les matchs terminés d'un championnat"""
    url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/last/0"
    data = fetch_json(driver, url)
    return data.get("events", [])
 
def get_incidents_match(driver, match_id):
    """Récupère les buts d'un match"""
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
    data = fetch_json(driver, url)
    return data.get("incidents", [])
 
def determiner_tranche(minute):
    """Détermine la tranche de 15 minutes d'un but"""
    if minute is None:
        return None
    if 0 <= minute <= 15:
        return "tranche_0_15"
    elif 16 <= minute <= 30:
        return "tranche_16_30"
    elif 31 <= minute <= 45:
        return "tranche_31_45"
    elif 46 <= minute <= 60:
        return "tranche_46_60"
    elif 61 <= minute <= 75:
        return "tranche_61_75"
    else:
        return "tranche_76_90"
 
def upsert_moment_but(id_equipe, stats):
    """Insère ou met à jour les stats dans Supabase"""
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/moment_but?id_equipe=eq.{id_equipe}",
        headers=HEADERS_SUPA
    ).json()
 
    if res:
        headers_update = {**HEADERS_SUPA, "Prefer": "return=minimal"}
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/moment_but?id_equipe=eq.{id_equipe}",
            headers=headers_update,
            json=stats
        )
    else:
        payload = {"id_equipe": id_equipe, **stats}
        requests.post(
            f"{SUPABASE_URL}/rest/v1/moment_but",
            headers=HEADERS_SUPA,
            json=payload
        )
 
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print(f"=== SCRAPING MOMENTS DE BUTS ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
 
# Charger toutes les équipes de la BDD
print("Chargement des équipes depuis Supabase...")
equipes_bdd = {}
for offset in [0, 1000]:
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/equipe?select=id_equipe,nom_equipe&offset={offset}&limit=1000",
        headers=HEADERS_SUPA
    ).json()
    for e in res:
        equipes_bdd[e["nom_equipe"]] = e["id_equipe"]
print(f"{len(equipes_bdd)} équipes chargées\n")
 
# Lancer le navigateur
print("Lancement du navigateur Chrome...")
driver = creer_driver()
 
# Visite Sofascore d'abord pour récupérer les cookies comme un humain
driver.get("https://www.sofascore.com/fr/")
time.sleep(random.uniform(3, 5))
print("Cookies récupérés ✅\n")
 
stats_equipes = {}
 
for nom_champi, infos in CHAMPIONNATS_SOFA.items():
    print(f"--- {nom_champi} ---")
    matchs = get_matchs_termines(driver, infos["tournament_id"], infos["season_id"])
    print(f"{len(matchs)} matchs récupérés")
 
    for match in matchs:
        match_id = match.get("id")
        home = match.get("homeTeam", {}).get("name", "")
        away = match.get("awayTeam", {}).get("name", "")
 
        incidents = get_incidents_match(driver, match_id)
 
        for incident in incidents:
            if incident.get("incidentType") != "goal":
                continue
            if incident.get("incidentClass") == "ownGoal":
                continue
 
            minute = incident.get("time")
            equipe_qui_marque = incident.get("isHome")
            nom_equipe = home if equipe_qui_marque else away
 
            id_equipe = None
            for nom_bdd, id_bdd in equipes_bdd.items():
                if nom_equipe.lower() in nom_bdd.lower() or nom_bdd.lower() in nom_equipe.lower():
                    id_equipe = id_bdd
                    break
 
            if not id_equipe:
                continue
 
            tranche = determiner_tranche(minute)
            if not tranche:
                continue
 
            if id_equipe not in stats_equipes:
                stats_equipes[id_equipe] = {
                    "tranche_0_15": 0,
                    "tranche_16_30": 0,
                    "tranche_31_45": 0,
                    "tranche_46_60": 0,
                    "tranche_61_75": 0,
                    "tranche_76_90": 0,
                    "total_buts": 0
                }
 
            stats_equipes[id_equipe][tranche] += 1
            stats_equipes[id_equipe]["total_buts"] += 1
 
    print(f"✅ {nom_champi} traité\n")
 
# Fermer le navigateur
driver.quit()
print("Navigateur fermé ✅\n")
 
# Enregistrement dans Supabase
print("--- ENREGISTREMENT DANS SUPABASE ---")
for id_equipe, stats in stats_equipes.items():
    upsert_moment_but(id_equipe, stats)
    print(f"✅ Équipe {id_equipe} — {stats['total_buts']} buts enregistrés")
 
print(f"\n✅ {len(stats_equipes)} équipes enregistrées dans moment_but")
print("=== FIN ===")