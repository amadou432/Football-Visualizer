import requests
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================

API_KEY = "f970e9d659494d75ac4e7c73a7b75783"

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"

CHAMPIONNATS = {
    "PL": "Premier League",
    "FL1": "Ligue 1",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga"
}

HEADERS = {
    "X-Auth-Token": API_KEY
}

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"  
}

# ============================================================
# API
# ============================================================

def get_matches(competition_code):
    try:
        url = f"https://api.football-data.org/v4/competitions/{competition_code}/matches?season=2025&status=FINISHED"

        r = requests.get(url, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print("\n API ERROR", r.status_code)
            print(r.text[:300])
            return []

        return r.json().get("matches", [])

    except Exception as e:
        print("\n Exception API :", e)
        return []

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
            timeout=30
        )

        if resp.status_code not in [200, 201]:
            print("\n SUPABASE :", resp.status_code)
            print(resp.text[:300])
            return False

        return True

    except Exception as e:
        print("\n Exception Supabase :", e)
        return False

# ============================================================
# MAIN
# ============================================================

print("\n🚀 Lancement...\n")

total_insert = 0

for code, league_name in CHAMPIONNATS.items():

    print("=" * 60)
    print(f" {league_name}")
    print("=" * 60)

    matchs = get_matches(code)

    print(f" Matchs récupérés : {len(matchs)}")

    if not matchs:
        continue

    matchs_equipes = defaultdict(list)

    # regroupement équipes
    for m in matchs:


        if m.get("status") != "FINISHED":
            continue

        home = m["homeTeam"]
        away = m["awayTeam"]

        matchs_equipes[home["id"]].append(m)
        matchs_equipes[away["id"]].append(m)

    # traitement équipes
    for team_id, liste_matchs in matchs_equipes.items():

        derniers = sorted(
            liste_matchs,
            key=lambda x: x["utcDate"],
            reverse=True
        )[:5]

        forme_data = []
        team_name = ""

        for m in derniers:

            home = m["homeTeam"]
            away = m["awayTeam"]

            score = m.get("score", {}).get("fullTime", {})

            score_home = score.get("home") or 0
            score_away = score.get("away") or 0

            est_domicile = (team_id == home["id"])

            if est_domicile:
                team_name = home["name"]
                buts_m = score_home
                buts_e = score_away
                adversaire = away["name"]
            else:
                team_name = away["name"]
                buts_m = score_away
                buts_e = score_home
                adversaire = home["name"]

            if buts_m > buts_e:
                resultat = "W"
            elif buts_m == buts_e:
                resultat = "D"
            else:
                resultat = "L"

            forme_data.append({
                "id_equipe": team_id,
                "team_name": team_name,
                "match_id": m["id"],
                "date": m["utcDate"][:10],
                "buts_marques": buts_m,
                "buts_encaisses": buts_e,
                "resultat": resultat,
                "domicile": est_domicile,
                "adversaire": adversaire
            })

        ok = envoyer_supabase(forme_data)

        if ok:
            total_insert += len(forme_data)
            print(f" {team_name} → OK ({len(forme_data)} matchs)")
        else:
            print(f" Insert KO {team_name}")

print("\n" + "=" * 60)
print(" TERMINÉ")
print(f" Lignes insérées : {total_insert}")
print("=" * 60)