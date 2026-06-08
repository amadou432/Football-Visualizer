
import requests
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
# ============================================================
# CONFIGURATION SUPABASE
# ============================================================
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"
 
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
 
# ============================================================
# CONFIGURATION CHAMPIONNATS SOFASCORE
# ============================================================
CHAMPIONNATS_SOFA = {
    "Premier League": {"tournament_id": 17,  "season_id": 76986},
    "Ligue 1":        {"tournament_id": 34,  "season_id": 77356},
    "La Liga":        {"tournament_id": 8,   "season_id": 77559},
    "Serie A":        {"tournament_id": 23,  "season_id": 76457},
    "Bundesliga":     {"tournament_id": 35,  "season_id": 77333},
}
 
# ============================================================
# MAPPING SofaScore → nom exact BDD
# Saison 2025/2026 — 96 équipes uniquement
# ============================================================
MAPPING_EQUIPES = {
 
    # -------------------------
    # PREMIER LEAGUE (20 clubs)
    # -------------------------
    "Arsenal":                     "Arsenal FC",
     "Leeds United":                     "Leeds United FC",
    "Aston Villa":                 "Aston Villa FC",
    "AFC Bournemouth":             "AFC Bournemouth",
    "Bournemouth":                 "AFC Bournemouth",
    "Brentford":                   "Brentford FC",
    "Brighton & Hove Albion":      "Brighton & Hove Albion FC",
    "Chelsea":                     "Chelsea FC",
    "Crystal Palace":              "Crystal Palace FC",
    "Everton":                     "Everton FC",
    "Fulham":                      "Fulham FC",
    "Ipswich Town":                "Ipswich Town FC",
    "Leicester City":              "Leicester City FC",
    "Liverpool FC":                   "Liverpool FC",
    "Manchester City":             "Manchester City FC",
    "Manchester United":           "Manchester United FC",
    "Newcastle United":            "Newcastle United FC",
    "Nottingham Forest":           "Nottingham Forest FC",
    "Southampton":                 "Southampton FC",
    "Tottenham Hotspur":           "Tottenham Hotspur FC",
    "West Ham United":             "West Ham United FC",
    "Wolverhampton":     "Wolverhampton Wanderers FC",
    "Burnley":                 "Burnley FC",
    "Sunderland":                 "Sunderland AFC",
    # -------------------------
    # LIGUE 1 (18 clubs)
    # -------------------------
    "Paris Saint-Germain":         "Paris Saint-Germain FC",
    "Paris FC":      "Paris FC",
    "Olympique de Marseille":      "Olympique de Marseille",
    "Marseille":                   "Olympique de Marseille",
    "Olympique Lyonnais":          "Olympique Lyonnais",
    "Lyon":                        "Olympique Lyonnais",
    "AS Monaco":                   "AS Monaco FC",
    "Monaco":                      "AS Monaco FC",
    "OGC Nice":                    "OGC Nice",
    "Nice":                        "OGC Nice",
    "Stade Rennais":            "Stade Rennais FC 1901",
    
    "RC Lens": "Racing Club de Lens",
    
    "Lille":                       "Lille OSC",
    "Montpellier HSC":             "Montpellier HSC",
    "Montpellier":                 "Montpellier HSC",
    "Stade de Reims":              "Stade de Reims",
    "Reims":                       "Stade de Reims",
    
    "Stade Brestois":                  "Stade Brestois 29",
    "RC Strasbourg":                  "RC Strasbourg Alsace",
    "FC Nantes":                   "FC Nantes",
    "Nantes":                      "FC Nantes",
    "Toulouse FC":                 "Toulouse FC",
    "Toulouse":                    "Toulouse FC",
    "AJ Auxerre":                  "AJ Auxerre",
    "Auxerre":                     "AJ Auxerre",
    "Angers SCO":                  "Angers SCO",
    "Angers":                      "Angers SCO",
    "AS Saint-Étienne":            "AS Saint-Étienne",
    "Saint-Etienne":               "AS Saint-Étienne",
    "Le Havre AC":                 "Le Havre AC",
    "Le Havre":                    "Le Havre AC",
    "Lorient":                    "FC Lorient",
    "Metz":                    "FC Metz",
     "Rodez AF":                    "",
    # -------------------------
    # LA LIGA (20 clubs)
    # -------------------------
    "Real Madrid":                 "Real Madrid CF",
    "FC Barcelona":                "FC Barcelona",
    "Barcelona":                   "FC Barcelona",
    "Atlético de Madrid":          "Club Atlético de Madrid",
    "Atlético Madrid":      "Club Atlético de Madrid", 
    "Athletic Club":               "Athletic Club",
    "Athletic Bilbao":             "Athletic Club",
    "Real Sociedad":               "Real Sociedad de Fútbol",
    "Villarreal CF":               "Villarreal CF",
    "Villarreal":                  "Villarreal CF",
    "Real Betis":                  "Real Betis Balompié",
    "Betis":                       "Real Betis Balompié",
    "Sevilla FC":                  "Sevilla FC",
    "Sevilla":                     "Sevilla FC",
    "Celta de Vigo":               "RC Celta de Vigo",
    "Celta Vigo":                  "RC Celta de Vigo",
    "Girona FC":                   "Girona FC",
    "Girona":                      "Girona FC",
    "Rayo Vallecano":              "Rayo Vallecano de Madrid",
    "Osasuna":                     "CA Osasuna",
    "CA Osasuna":                  "CA Osasuna",
    "Getafe CF":                   "Getafe CF",
    "Getafe":                      "Getafe CF",
    "Deportivo Alavés":            "Deportivo Alavés",
    "Alavés":                      "Deportivo Alavés",
    "Valencia CF":                 "Valencia CF",
    "Valencia":                    "Valencia CF",
    "UD Las Palmas":               "UD Las Palmas",
    "Las Palmas":                  "UD Las Palmas",
    "Leganés":                     "CD Leganés",
    "Elche":                     "Elche CF",
    "CD Leganés":                  "CD Leganés",
    "RCD Espanyol":                "RCD Espanyol de Barcelona",
    "Espanyol":                    "RCD Espanyol de Barcelona",
    "RCD Mallorca":                "RCD Mallorca",
    "Mallorca":                    "RCD Mallorca",
    "Real Valladolid":             "Real Valladolid CF",
    "Levante UD":             "Levante UD",
    "Real Oviedo":             "Real Oviedo",
    # -------------------------
    # SERIE A (20 clubs)
    # -------------------------
    "Inter":                       "FC Internazionale Milano",
    "Internazionale":              "FC Internazionale Milano",
    "Inter Milan":                 "FC Internazionale Milano",
    "AC Milan":                    "AC Milan",
    "Milan":                       "AC Milan",
    "Juventus":                    "Juventus FC",
    "Napoli":                      "SSC Napoli",
    "SSC Napoli":                  "SSC Napoli",
    "AS Roma":                     "AS Roma",
    "Roma":                        "AS Roma",
    "SS Lazio":                    "SS Lazio",
    "Lazio":                       "SS Lazio",
    "Atalanta":                    "Atalanta BC",
    "Atalanta BC":                 "Atalanta BC",
    "Fiorentina":                  "ACF Fiorentina",
    "ACF Fiorentina":              "ACF Fiorentina",
    "Bologna":                     "Bologna FC 1909",
    "Bologna FC":                  "Bologna FC 1909",
    "Torino":                      "Torino FC",
    "Torino FC":                   "Torino FC",
    "Udinese":                     "Udinese Calcio",
    "Udinese Calcio":              "Udinese Calcio",
    "Empoli":                      "Empoli FC",
    "Empoli FC":                   "Empoli FC",
    "Hellas Verona":               "Hellas Verona FC",
    "Verona":                      "Hellas Verona FC",
    "Cagliari":                    "Cagliari Calcio",
    "Cagliari Calcio":             "Cagliari Calcio",
    "Lecce":                       "US Lecce",
    "US Lecce":                    "US Lecce",
    "Genoa":                       "Genoa CFC",
    "Genoa CFC":                   "Genoa CFC",
    "Monza":                       "AC Monza",
    "AC Monza":                    "AC Monza",
    "Venezia":                     "Venezia FC",
    "Como":                        "Como 1907",
    "Parma":                       "Parma Calcio 1913",
    "Cremonese":                       "US Cremonese",
    "Pisa":                       "AC Pisa 1909",
    "Sassuolo":                       "US Sassuolo Calcio",
    # -------------------------
    # BUNDESLIGA (18 clubs)
    # -------------------------
    "1. FC Köln":           "1. FC Köln",
    "FC Bayern München":           "FC Bayern München",
    "Bayern Munich":               "FC Bayern München",
    "Bayern München":              "FC Bayern München",
    "Bayer 04 Leverkusen":         "Bayer 04 Leverkusen",
    "Leverkusen":                  "Bayer 04 Leverkusen",
    "Borussia Dortmund":           "Borussia Dortmund",
    "RB Leipzig":                  "RB Leipzig",
    "Borussia M'gladbach":      "Borussia Mönchengladbach",
    "Eintracht Frankfurt":         "Eintracht Frankfurt",
    "TSG 1899 Hoffenheim":         "TSG 1899 Hoffenheim",
    "TSG Hoffenheim":              "TSG 1899 Hoffenheim",
    "Hoffenheim":                  "TSG 1899 Hoffenheim",
    "SC Freiburg":                 "SC Freiburg",
    "Freiburg":                    "SC Freiburg",
    "VfB Stuttgart":               "VfB Stuttgart",
    "Stuttgart":                   "VfB Stuttgart",
    "VfL Wolfsburg":               "VfL Wolfsburg",
    "Wolfsburg":                   "VfL Wolfsburg",
    "1. FC Union Berlin":          "1. FC Union Berlin",
    "Union Berlin":                "1. FC Union Berlin",
    "SV Werder Bremen":            "SV Werder Bremen",
    "Werder Bremen":               "SV Werder Bremen",
    "FC Augsburg":                 "FC Augsburg",
    "Augsburg":                    "FC Augsburg",
    "1. FSV Mainz 05":             "1. FSV Mainz 05",
    "Mainz 05":                    "1. FSV Mainz 05",
    "VfL Bochum":                  "VfL Bochum 1848",
    "Bochum":                      "VfL Bochum 1848",
    "Holstein Kiel":               "Holstein Kiel",
    "FC St. Pauli":                "FC St. Pauli 1910",
    "St. Pauli":                   "FC St. Pauli 1910",
    "1. FC Heidenheim 1846":       "1. FC Heidenheim 1846",
    "Heidenheim":                  "1. FC Heidenheim 1846",
    "1. FC Heidenheim":            "1. FC Heidenheim 1846",
    "Hamburger SV":                    "Hamburger SV",
}
 
# ============================================================
# DRIVER SELENIUM
# ============================================================
def creer_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver
 
# ============================================================
# FETCH JSON
# ============================================================
def fetch_json(driver, url):
    driver.get(url)
    time.sleep(random.uniform(2, 4))
    try:
        body = driver.find_element("tag name", "body").text
        return json.loads(body)
    except:
        return {}
 
# ============================================================
# RÉCUPÉRATION DE TOUS LES MATCHS D'UNE SAISON
# ============================================================
def get_tous_les_matchs(driver, tournament_id, season_id):
    tous_les_matchs = []
    page = 0
    while True:
        url = f"https://api.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/last/{page}"
        data = fetch_json(driver, url)
        events = data.get("events", [])
        if not events:
            print(f"      Page {page} vide — arrêt ({len(tous_les_matchs)} matchs au total)")
            break
        tous_les_matchs.extend(events)
        print(f"      Page {page} → {len(events)} matchs récupérés (total: {len(tous_les_matchs)})")
        page += 1
        if page > 20:
            print(f"      Limite de 20 pages atteinte")
            break
    return tous_les_matchs
 
# ============================================================
# RÉCUPÉRATION DES INCIDENTS D'UN MATCH
# ============================================================
def get_incidents_match(driver, match_id):
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
    data = fetch_json(driver, url)
    return data.get("incidents", [])
 
# ============================================================
# RÉSOLUTION NOM ÉQUIPE → id_equipe BDD
# ============================================================
def resoudre_equipe(nom_sofa, equipes_bdd):
    """
    Vérifie uniquement le mapping exact pour éviter les fausses
    associations avec des équipes hors des 5 grands championnats.
    """
    nom_mappe = MAPPING_EQUIPES.get(nom_sofa)
    if nom_mappe and nom_mappe in equipes_bdd:
        return equipes_bdd[nom_mappe]
    
    # On a supprimé la boucle for globale "in" qui venait polluer les championnats
    return None
 
# ============================================================
# CHARGEMENT DES ÉQUIPES DEPUIS SUPABASE
# ============================================================
def charger_equipes():
    equipes_bdd = {}
    for offset in [0, 1000]:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/equipe?select=id_equipe,nom_equipe&offset={offset}&limit=1000",
            headers=HEADERS_SUPA
        ).json()
        for e in res:
            equipes_bdd[e["nom_equipe"]] = e["id_equipe"]
    return equipes_bdd
 
# ============================================================
# UPSERT GÉNÉRIQUE SUPABASE (avec retry)
# ============================================================
def upsert_supabase(table, filtre_col, filtre_val, payload, tentatives=3):
    for tentative in range(tentatives):
        try:
            res = requests.get(
                f"{SUPABASE_URL}/rest/v1/{table}?{filtre_col}=eq.{filtre_val}",
                headers=HEADERS_SUPA,
                timeout=15
            ).json()
 
            if res:
                headers_update = {**HEADERS_SUPA, "Prefer": "return=minimal"}
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/{table}?{filtre_col}=eq.{filtre_val}",
                    headers=headers_update,
                    json=payload,
                    timeout=15
                )
            else:
                requests.post(
                    f"{SUPABASE_URL}/rest/v1/{table}",
                    headers=HEADERS_SUPA,
                    json={filtre_col: filtre_val, **payload},
                    timeout=15
                )
            return
 
        except Exception as e:
            print(f"   ⚠️  Tentative {tentative+1}/{tentatives} échouée : {e}")
            if tentative < tentatives - 1:
                time.sleep(5)
            else:
                print(f"   ❌ {table} / {filtre_col}={filtre_val} non enregistré après {tentatives} tentatives")