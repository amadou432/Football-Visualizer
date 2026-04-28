import requests
from flask import Flask, render_template
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEYS = [
    os.getenv("API_KEY_1"),
    os.getenv("API_KEY_2"),
    os.getenv("API_KEY_3")
]

BASE_URL = "https://v3.football.api-sports.io"


def api_request(endpoint):
    for key in API_KEYS:
        if not key:
            continue

        headers = {"x-apisports-key": key.strip()}

        try:
            response = requests.get(BASE_URL + endpoint, headers=headers, timeout=5)

            if response.status_code != 200:
                continue

            data = response.json()

            if data.get("errors"):
                continue

            return data

        except requests.exceptions.RequestException:
            continue

    return None


# 🔥 HOME PAGE
@app.route('/')
def home():
    today = datetime.today().strftime('%Y-%m-%d')

    data = api_request(f"/fixtures?date={today}")

    matchs = data.get("response", []) if data else []

    return render_template("home.html", matchs=matchs, error=(not data))


# 🔥 MATCH PAGE
@app.route('/match/<int:match_id>')
def match_details(match_id):

    data = api_request(f"/fixtures?id={match_id}")

    if not data or not data.get("response"):
        return "Match non trouvé", 404

    fixture = data["response"][0]

    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]

    # ⚠️ placeholder clean (plus tard remplacé par vraie logique)
    context = {
        "fixture": fixture,
        "status": fixture["fixture"]["status"]["long"],

        # ✔️ toujours safe (pas fake hardcodé dans template)
        "home_forme": [],
        "away_forme": [],

        "cotes": None,
        "home_indice": 50,
        "away_indice": 50
    }

    return render_template("match.html", **context)


# 🔥 DEBUG API
@app.route('/debug')
def debug_api():
    return api_request("/status") or {"error": "API KO"}


if __name__ == '__main__':
    app.run(debug=True)