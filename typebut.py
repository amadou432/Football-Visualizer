import requests
import time
import random
from collections import defaultdict
from datetime import datetime, timezone

from base import creer_driver, fetch_json, get_tous_les_matchs

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

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# ============================================================
# INCIDENTS AVEC RÉCUPÉRATION AUTO DU DRIVER
# ============================================================

def get_incidents_safe(driver, event_id):
    """Récupère les incidents d'un match. Recrée le driver si il crash."""
    try:
        url = f"https://api.sofascore.com/api/v1/event/{event_id}/incidents"
        data = fetch_json(driver, url)
        return data.get("incidents", []), driver

    except Exception as e:
        print(f"⚠️ Driver mort ({e.__class__.__name__}), relance...")

        # Ferme l'ancien driver proprement
        try:
            driver.quit()
        except:
            pass

        # Recrée un nouveau driver et revisite la home
        new_driver = creer_driver()
        new_driver.get("https://www.sofascore.com/fr/")
        time.sleep(random.uniform(2, 4))

        # Réessaie avec le nouveau driver
        try:
            url = f"https://api.sofascore.com/api/v1/event/{event_id}/incidents"
            data = fetch_json(new_driver, url)
            print("✅ Driver relancé avec succès")
            return data.get("incidents", []), new_driver
        except Exception as e2:
            print(f"❌ Échec après relance : {e2}")
            return [], new_driver

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

total_lignes = 0

for key, league in CHAMPIONNATS.items():

    print("\n==============================")
    print(f"Ligue : {league['name']}")
    print("==============================")

    # Crée le driver et visite la home pour initialiser les cookies
    driver = creer_driver()
    driver.get("https://www.sofascore.com/fr/")
    time.sleep(random.uniform(2, 4))

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

        # ✅ get_incidents_safe retourne aussi le driver (potentiellement recréé)
        incidents, driver = get_incidents_safe(driver, event_id)

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

        # Délai aléatoire entre chaque match
        time.sleep(random.uniform(2.0, 5.0))

        # Log de progression toutes les 20 requêtes
        if (idx + 1) % 20 == 0:
            print(f"  → {idx + 1}/{len(matchs)} matchs traités")

    # Ferme le driver proprement après chaque ligue
    try:
        driver.quit()
    except:
        pass

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

    print(f"\nPause avant la prochaine ligue...")
    time.sleep(random.uniform(3, 6))

print("\n✅ FIN")
print(f"Total lignes envoyées : {total_lignes}")
