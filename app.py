import requests
from flask import Flask, render_template

app = Flask(__name__)

API_KEY = "dd544001be70456d8a98135cdee965e1" 
HEADERS = {
    'x-apisports-key': API_KEY,
    'Content-Type': 'application/json'
}

@app.route('/')
def home():
   
    url = "https://v3.football.api-sports.io/fixtures?date=2024-04-24"
    response = requests.get(url, headers=HEADERS).json()
    
 
    print("DEBUG API:", response) 
    
    matches_list = response.get('response', [])
    return render_template('home.html', matches=matches_list)
@app.route('/match/<int:match_id>')
def match_details(match_id):
    url = f"https://v3.football.api-sports.io/fixtures?id={match_id}"
    response = requests.get(url, headers=HEADERS).json()
    fixture_data = response['response'][0] if response.get('response') else None

    if not fixture_data:
        return "Match non trouvé", 404

    context = {
        "fixture": fixture_data,
        "status": fixture_data['fixture']['status']['long'],
        "home_forme": ['W', 'W', 'D', 'L', 'W'], 
        "away_forme": ['L', 'D', 'W', 'L', 'L'], 
        "cotes": {"home": 1.85, "draw": 3.40, "away": 4.20},
        "home_indice": 65, 
        "away_indice": 35
    }
    return render_template('match.html', **context)

if __name__ == '__main__':
    app.run(debug=True)