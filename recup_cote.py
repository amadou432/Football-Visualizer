
import requests
from datetime import datetime

API_KEY = "425703d19e8715045f7903061b68971c"
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Les 5 grands championnats
LIGUES = [39, 61, 140, 135, 78]

date_du_jour = datetime.now().strftime('%Y-%m-%d')

print(f"--- Récupération des cotes pour le {date_du_jour} ---")

# Récupération des cotes
response = requests.get(
    "https://v3.football.api-sports.io/odds",
    headers={"x-apisports-key": API_KEY},
    params={"date": date_du_jour, "bet": 1}
)
data = response.json()

# Filtrer les 5 grands championnats
matchs_avec_cotes = [item for item in data.get('response', []) if item['league']['id'] in LIGUES]

if not matchs_avec_cotes:
    print("Pas de cotes disponibles aujourd'hui.")
else:
    print(f"{len(matchs_avec_cotes)} matchs avec cotes trouvés.")

    liste_cotes = []

    for item in matchs_avec_cotes:
        id_match = item['fixture']['id']
        bookmakers = item['bookmakers']

        best_1, bookie_1 = 0.0, ""
        best_n, bookie_n = 0.0, ""
        best_2, bookie_2 = 0.0, ""

        for bookie in bookmakers:
            for bet in bookie['bets']:
                if bet['name'] == "Match Winner":
                    odds = {v['value']: float(v['odd']) for v in bet['values']}

                    c1 = odds.get('Home', 0)
                    cn = odds.get('Draw', 0)
                    c2 = odds.get('Away', 0)

                    if c1 > best_1:
                        best_1 = c1
                        bookie_1 = bookie['name']

                    if cn > best_n:
                        best_n = cn
                        bookie_n = bookie['name']

                    if c2 > best_2:
                        best_2 = c2
                        bookie_2 = bookie['name']

        if best_1 > 0:
            liste_cotes.append({
                "id_match": id_match,
                "cote_1": best_1,
                "bookmaker_1": bookie_1,
                "cote_n": best_n,
                "bookmaker_n": bookie_n,
                "cote_2": best_2,
                "bookmaker_2": bookie_2
            })

            print(f" Match {id_match}")
            print(f"   Victoire DOM : {best_1} chez {bookie_1}")
            print(f"   Match Nul    : {best_n} chez {bookie_n}")
            print(f"   Victoire EXT : {best_2} chez {bookie_2}")
            print("-" * 40)

    # Envoi vers Supabase
    if liste_cotes:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/cote",
            headers=HEADERS_SUPA,
            json=liste_cotes
        )

        if res.status_code in [200, 201, 204]:
            print(f" RÉUSSITE ! {len(liste_cotes)} cotes stockées dans Supabase.")
        else:
            print(f" Erreur : {res.text}")

print("--- Fin du script ---")