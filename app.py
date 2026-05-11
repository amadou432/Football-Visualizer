import requests
from flask import Flask, render_template
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# On récupère tes 3 clés
API_KEYS = [os.getenv("API_KEY_1"), os.getenv("API_KEY_2"), os.getenv("API_KEY_3")]
API_KEYS = [k for k in API_KEYS if k]

def api_request(endpoint):
    for key in API_KEYS:
        key = key.strip()
        
        # SI LA CLÉ VIENT DE RAPIDAPI (Format avec 'msh' ou 'jsn')
        if "msh" in key or len(key) > 40: 
            url = f"https://api-football-v1.p.rapidapi.com/v3{endpoint}"
            headers = {
                "x-rapidapi-key": key,
                "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
            }
        # SI LA CLÉ VIENT D'API-SPORTS DIRECT (Format standard 32 caractères)
        else:
            url = f"https://v3.football.api-sports.io{endpoint}"
            headers = {"x-apisports-key": key}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # On vérifie que l'API ne renvoie pas d'erreur de quota
                if not data.get("errors"):
                    return data
            print(f"Échec avec la clé {key[:10]}... sur l'URL {url}")
        except:
            continue
    return None

def get_clean_form(stats_data):
    if not stats_data or "response" not in stats_data:
        return []
    form_str = stats_data["response"].get("form", "") or ""
    translated = form_str.replace('W','V').replace('L','D').replace('D','N')
    return list(translated)[-5:]

@app.route('/')
def home():
    today = datetime.today().strftime('%Y-%m-%d')
    data = api_request(f"/fixtures?date={today}")
    matchs = data.get("response", []) if data else []
    # Si data est None, l'erreur jaune s'affiche
    return render_template("home.html", matchs=matchs, error=(not data))

@app.route('/match/<int:match_id>')
def match_details(match_id):
    data = api_request(f"/fixtures?id={match_id}")
    if not data or not data.get("response"):
        return "Match non trouvé", 404

    fixture = data["response"][0]
    h_id = fixture["teams"]["home"]["id"]
    a_id = fixture["teams"]["away"]["id"]
    league = fixture["league"]["id"]
    season = fixture["league"]["season"]

    h_stats = api_request(f"/teams/statistics?league={league}&season={season}&team={h_id}")
    a_stats = api_request(f"/teams/statistics?league={league}&season={season}&team={a_id}")

    # Calcul de l'indice basé sur les victoires réelles
    h_wins = h_stats["response"]["fixtures"]["wins"]["total"] if h_stats and h_stats.get("response") else 0
    a_wins = a_stats["response"]["fixtures"]["wins"]["total"] if a_stats and a_stats.get("response") else 0
    
    total = h_wins + a_wins
    h_idx = int((h_wins / total) * 100) if total > 0 else 50
    a_idx = 100 - h_idx

    context = {
        "fixture": fixture,
        "status": fixture["fixture"]["status"]["long"],
        "home_forme": get_clean_form(h_stats),
        "away_forme": get_clean_form(a_stats),
        "home_indice": h_idx,
        "away_indice": a_idx,
        "lineups": api_request(f"/fixtures/lineups?fixture={match_id}").get("response", []) if h_id else []
    }
    return render_template("match.html", **context)

if __name__ == '__main__':
    app.run(debug=True)