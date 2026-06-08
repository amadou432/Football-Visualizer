import requests
import time
import random
from collections import defaultdict
from datetime import datetime, timezone

from base import creer_driver, get_tous_les_matchs

# ============================================================
# CONFIG
# ============================================================

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"

CHAMPIONNATS = {
    "PL":  {"id": 17, "season": 76986, "name": "Premier League"},
    "FL1": {"id": 34, "season": 77356, "name": "Ligue 1"},
    "PD":  {"id": 8, "season": 77559, "name": "La Liga"},
    "SA":  {"id": 23, "season": 76457, "name": "Serie A"},
    "BL1": {"id": 35, "season": 77333, "name": "Bundesliga"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "same-site",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Dest": "empty",
"Referer": "https://www.sofascore.com/"
}

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# ============================================================
# SESSION PERSISTANTE
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)

def init_session():
    """Visite la home pour initialiser les cookies comme un vrai navigateur."""
    print("Initialisation de la session SofaScore...")
    try:
        session.get("https://www.sofascore.com/", timeout=30)
        print("Session initialisée ✓")
    except Exception as e:
        print(f"Avertissement init session : {e}")
    time.sleep(random.uniform(1.5, 2.5))

# ============================================================
# SAFE REQUEST
# ============================================================

def safe_get(url, retries=4):
    for i in range(retries):
        try:
            r = session.get(url, timeout=30)

            if r.status_code == 200:
                return r

            if r.status_code == 403:
                wait = 3 * (i + 1) + random.uniform(0.5, 1.5)
                print(f"403 détecté → retry {i + 1}/{retries}, attente {wait:.1f}s")
                time.sleep(wait)

            elif r.status_code == 429:
                wait = 10 + random.uniform(2, 5)
                print(f"429 rate limit → attente {wait:.1f}s")
                time.sleep(wait)

            else:
                print(f"API error : {r.status_code}")
                time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau : {e}")
            time.sleep(3)

    return None

# ============================================================
# INCIDENTS
# ============================================================

def get_incidents(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/incidents"

    r = safe_get(url)

    if not r:
        return []

    try:
        return r.json().get("incidents", [])
    except Exception as e:
        print(f"Erreur JSON incidents {event_id} : {e}")
        return []

# ============================================================
# SUPABASE
# ============================================================

def send_supabase(data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/types_buts_equipes",
        headers=SUPA_HEADERS,
        json=data,
        timeout=30
    )

    if r.status_code not in (200, 201):
        print(f"SUPABASE ERROR : {r.status_code}")
        print(r.text[:300])
        return False

    return True

# ============================================================
# UTIL
# ============================================================

def pct(val, total):
    return round(val / total * 100, 2) if total else 0.0

# ============================================================
# MAIN
# ============================================================

print("\n▶ START\n")

# Initialisation de la session AVANT toute requête API
init_session()

total_lignes = 0

for key, league in CHAMPIONNATS.items():

    print("\n==============================")
    print(f"Ligue : {league['name']}")
    print("==============================")

    
    driver = creer_driver()
    driver.get("https://www.sofascore.com/fr/")
    print(driver, league["id"], league["season"])
    matchs = get_tous_les_matchs(driver, league["id"], league["season"])
    print(f"Matchs récupérés : {len(matchs)}")

    stats = defaultdict(lambda: {
        "nom": "",
        "penalty": 0,
        "coup_franc": 0,
        "csc": 0,
        "autres": 0,
        "tete": 0,
        "gauche": 0,
        "droite": 0,
        "total": 0,
    })

    # ========================================================
    # MATCH LOOP
    # ========================================================

    for idx, m in enumerate(matchs):

        event_id = m.get("id")
        if not event_id:
            continue

        incidents = get_incidents(event_id)

        for inc in incidents:

            if inc.get("incidentType") != "goal":
                continue

            team = inc.get("scoringTeam")
            if not team:
                continue

            team_id = team["id"]
            team_name = team["name"]

            s = stats[team_id]
            s["nom"] = team_name
            s["total"] += 1

            goal_type = (inc.get("goalType") or "").lower()

            if goal_type == "penalty":
                s["penalty"] += 1
            elif goal_type == "own":
                s["csc"] += 1
            elif goal_type in ("free-kick", "freekick"):
                s["coup_franc"] += 1
            else:
                s["autres"] += 1

            shot_type = (inc.get("shotType") or "").lower()

            if shot_type == "header":
                s["tete"] += 1
            elif shot_type == "left-foot":
                s["gauche"] += 1
            elif shot_type == "right-foot":
                s["droite"] += 1

        # Délai aléatoire entre chaque match (bien plus long qu'avant)
        time.sleep(random.uniform(2.0, 5.0))

        # Log de progression toutes les 20 requêtes
        if (idx + 1) % 20 == 0:
            print(f"  → {idx + 1}/{len(matchs)} matchs traités")

    # ========================================================
    # SUPABASE
    # ========================================================

    batch = []
    now = datetime.now(timezone.utc).isoformat()

    for team_id, s in stats.items():

        if s["total"] == 0:
            continue

        t = s["total"]

        batch.append({
            "id_equipe": team_id,
            "nom_equipe": s["nom"],
            "id_saison": league["season"],
            "id_tournoi": league["id"],

            "total_buts": t,

            "buts_penalty": s["penalty"],
            "buts_coup_franc": s["coup_franc"],
            "buts_contre_son_camp": s["csc"],
            "buts_autres": s["autres"],

            "buts_tete": s["tete"],
            "buts_pied_gauche": s["gauche"],
            "buts_pied_droit": s["droite"],

            "pourcentage_buts_penalty": pct(s["penalty"], t),
            "pourcentage_buts_coup_franc": pct(s["coup_franc"], t),
            "pourcentage_buts_csc": pct(s["csc"], t),
            "pourcentage_buts_autres": pct(s["autres"], t),

            "pourcentage_buts_tete": pct(s["tete"], t),
            "pourcentage_buts_pied_gauche": pct(s["gauche"], t),
            "pourcentage_buts_pied_droit": pct(s["droite"], t),

            "date_mise_a_jour": now,
        })

    if batch:
        ok = send_supabase(batch)

        if ok:
            total_lignes += len(batch)
            for r in batch:
                print(f"OK : {r['nom_equipe']}")
        else:
            print(f"Erreur Supabase pour {league['name']}")

    # Pause entre chaque ligue
    print(f"\nPause avant la prochaine ligue...")
    time.sleep(random.uniform(3, 6))

print("\n✅ FIN")
print(f"Total lignes envoyées : {total_lignes}")