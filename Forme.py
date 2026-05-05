import requests
import time

# ============================================================
# CONFIG
# ============================================================
API_FOOTBALL_KEY = "29a980f4b9c56ba437b5f050b007ce69"
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"

CHAMPIONNATS = [
    {"league_id": 39, "name": "Premier League", "season": 2024},
    {"league_id": 61, "name": "Ligue 1", "season": 2024},
    {"league_id": 140, "name": "La Liga", "season": 2024},
    {"league_id": 135, "name": "Serie A", "season": 2024},
    {"league_id": 78, "name": "Bundesliga", "season": 2024},
]

API_HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_FOOTBALL_KEY
}

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}


# ============================================================
# API FOOTBALL
# ============================================================
def get_api(endpoint, params=None):
    try:
        r = requests.get(
            f"https://v3.football.api-sports.io/{endpoint}",
            headers=API_HEADERS,
            params=params,
            timeout=20
        )

        if r.status_code != 200:
            print(f" API ERROR {r.status_code}")
            print(r.text[:300])
            return []

        data = r.json()

        if data.get("errors"):
            print(" API ERROR :", data["errors"])
            return []

        return data.get("response", [])

    except Exception as e:
        print(" Exception API :", e)
        return []


def appels_restants():
    try:
        r = requests.get(
            "https://v3.football.api-sports.io/status",
            headers=API_HEADERS,
            timeout=20
        )

        data = r.json().get("response", {})
        current = data.get("requests", {}).get("current", 0)
        limit = data.get("requests", {}).get("limit_day", 100)

        return limit - current

    except:
        return 0


# ============================================================
# SUPABASE
# ============================================================
def envoyer_supabase(data):
    if not data:
        return True

    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/forme_equipes",
            headers=SUPA_HEADERS,
            json=data,
            timeout=20
        )

        if resp.status_code not in [200, 201]:
            print(" SUPABASE :", resp.status_code, resp.text[:200])
            return False

        return True

    except Exception as e:
        print(" Exception Supabase :", e)
        return False


# ============================================================
# MAIN
# ============================================================
print("\n Lancement...\n")

restants = appels_restants()
print(f" Quota restant : {restants}/100")

if restants <= 10:
    print(" Pas assez d'appels API")
    exit()

print("\n Récupération des équipes...\n")

toutes_equipes = []

for champ in CHAMPIONNATS:
    print(f"→ {champ['name']}")

    equipes = get_api("teams", {
        "league": champ["league_id"],
        "season": champ["season"]
    })

    print(f"   {len(equipes)} équipes")

    for e in equipes:
        toutes_equipes.append({
            "team_id": e["team"]["id"],
            "team_name": e["team"]["name"],
            "league": champ["name"],
            "league_id": champ["league_id"],
            "season": champ["season"]
        })

print(f"\n {len(toutes_equipes)} équipes récupérées")

if not toutes_equipes:
    print(" Aucune équipe")
    exit()

# quota sécurité
max_teams = restants - 5
toutes_equipes = toutes_equipes[:max_teams]

print(f"\n Traitement de {len(toutes_equipes)} équipes...\n")

total_insert = 0

for i, equipe in enumerate(toutes_equipes):
    team_id = equipe["team_id"]
    team_name = equipe["team_name"]
    league_id = equipe["league_id"]
    season = equipe["season"]

    print(f"[{i+1}/{len(toutes_equipes)}] {team_name}...", end=" ")

    # récupère les matchs du championnat seulement
    matchs = get_api("fixtures", {
        "team": team_id,
        "league": league_id,
        "season": season,
        "status": "FT"
    })

    if not matchs:
        print("aucun match")
        continue

    # 5 derniers
    derniers = sorted(
        matchs,
        key=lambda x: x["fixture"]["date"],
        reverse=True
    )[:5]

    forme_data = []

    for m in derniers:
        home_id = m["teams"]["home"]["id"]
        home_name = m["teams"]["home"]["name"]
        away_name = m["teams"]["away"]["name"]

        home_goals = m["goals"]["home"] or 0
        away_goals = m["goals"]["away"] or 0

        est_domicile = (team_id == home_id)

        if est_domicile:
            buts_m = home_goals
            buts_e = away_goals
            adversaire = away_name
        else:
            buts_m = away_goals
            buts_e = home_goals
            adversaire = home_name

        if buts_m > buts_e:
            resultat = "W"
        elif buts_m == buts_e:
            resultat = "D"
        else:
            resultat = "L"

        forme_data.append({
            "team_id": team_id,
            "team_name": team_name,
            "match_id": m["fixture"]["id"],
            "date": m["fixture"]["date"][:10],
            "buts_marques": buts_m,
            "buts_encaisses": buts_e,
            "resultat": resultat,
            "domicile": est_domicile,
            "adversaire": adversaire
        })

    ok = envoyer_supabase(forme_data)

    if ok:
        total_insert += len(forme_data)
        forme = " ".join([x["resultat"] for x in forme_data])
        print(f" {forme}")
    else:
        print(" insert KO")

    time.sleep(0.3)

print("\n" + "=" * 50)
print(" TERMINÉ")
print("Équipes traitées :", len(toutes_equipes))
print("Lignes insérées :", total_insert)
print("=" * 50)