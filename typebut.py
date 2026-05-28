import requests
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"

CHAMPIONNATS = {
    "PL": {"id": 17, "season": 76986, "name": "Premier League"},
    "FL1": {"id": 34, "season": 77356, "name": "Ligue 1"},
    "PD": {"id": 8, "season": 77559, "name": "La Liga"},
    "SA": {"id": 23, "season": 76457, "name": "Serie A"},
    "BL1": {"id": 35, "season": 77333, "name": "Bundesliga"}
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/"
}

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}



def get_matches(tournament_id, season_id):

    url = (
        f"https://api.sofascore.com/api/v1/"
        f"unique-tournament/{tournament_id}/"
        f"season/{season_id}/events"
    )

    r = requests.get(url, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        print("API ERROR MATCHS :", r.status_code)
        return []

    return r.json().get("events", [])



def get_incidents(event_id):

    url = f"https://api.sofascore.com/api/v1/event/{event_id}/incidents"

    r = requests.get(url, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        return []

    return r.json().get("incidents", [])



def send_supabase(data):

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/type_but_equipes",
        headers=SUPA_HEADERS,
        json=data
    )

    if r.status_code not in [200, 201]:
        print("SUPABASE ERROR :", r.status_code)
        print(r.text[:200])
        return False

    return True



print("\n START...\n")

total = 0

for key, league in CHAMPIONNATS.items():

    print("=" * 50)
    print("Ligue :", league["name"])
    print("=" * 50)

    matchs = get_matches(league["id"], league["season"])

    print("Matchs :", len(matchs))

    stats = defaultdict(lambda: {
        "nom": "",
        "total": 0,
        "normal": 0,
        "penalty": 0,
        "csc": 0,
        "tete": 0,
        "gauche": 0,
        "droite": 0
    })

    for m in matchs:

        event_id = m.get("id")
        if not event_id:
            continue

        incidents = get_incidents(event_id)

        for i in incidents:

            if i.get("incidentType") != "goal":
                continue

            team = i.get("scoringTeam")
            if not team:
                continue

            team_id = team["id"]
            team_name = team["name"]

            s = stats[team_id]
            s["nom"] = team_name
            s["total"] += 1

            goal_type = (i.get("goalType") or "").lower()
            shot_type = (i.get("shotType") or "").lower()

            if goal_type == "penalty":
                s["penalty"] += 1
            elif goal_type == "own":
                s["csc"] += 1
            else:
                s["normal"] += 1

            if shot_type == "header":
                s["tete"] += 1
            elif shot_type == "left-foot":
                s["gauche"] += 1
            elif shot_type == "right-foot":
                s["droite"] += 1

    
    for team_id, s in stats.items():

        if s["total"] == 0:
            continue

        data = {
            "id_equipe": team_id,
            "nom_equipe": s["nom"],
            "competition": league["name"],

            "total_buts": s["total"],

            "buts_normaux": s["normal"],
            "buts_penalty": s["penalty"],
            "buts_csc": s["csc"],

            "buts_tete": s["tete"],
            "buts_pied_gauche": s["gauche"],
            "buts_pied_droit": s["droite"],

            "pct_normaux": round(s["normal"] / s["total"] * 100, 2),
            "pct_penalty": round(s["penalty"] / s["total"] * 100, 2),
            "pct_csc": round(s["csc"] / s["total"] * 100, 2),

            "pct_tete": round(s["tete"] / s["total"] * 100, 2),
            "pct_gauche": round(s["gauche"] / s["total"] * 100, 2),
            "pct_droite": round(s["droite"] / s["total"] * 100, 2),
        }

        ok = send_supabase([data])

        if ok:
            total += 1
            print("OK :", s["nom"])

print("\nFIN")
print("Lignes :", total)