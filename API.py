from flask import Flask, render_template
import requests
from datetime import datetime
 
app = Flask(__name__)
 
API_KEY = "b49cd48ad7f439af314355b5991ff713"
URL_BASE = "https://v3.football.api-sports.io"
HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_KEY
}
 
def get_json(endpoint, params):
    try:
        r = requests.get(f"{URL_BASE}/{endpoint}", headers=HEADERS, params=params)
        return r.json().get('response', [])
    except:
        return []
 
# ---- PAGE HOME (inchangée) ----
@app.route('/')
def home():
    date_du_jour = datetime.now().strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{URL_BASE}/fixtures", headers=HEADERS, params={'date': date_du_jour})
        data = response.json()
        matchs = data.get('response', [])
        matchs = sorted(matchs, key=lambda x: x['league']['id'])[:21]
    except Exception as e:
        print(f"Erreur : {e}")
        matchs = []
    return render_template('home.html', matchs=matchs)
 
 
# ---- PAGE MATCH DETAILS ----
@app.route('/match/<int:fixture_id>')
def match(fixture_id):
 
    # 1. Infos du match
    fixture_list = get_json('fixtures', {'id': fixture_id})
    fixture = fixture_list[0] if fixture_list else {}
    if not fixture:
        return "Match introuvable", 404
 
    home_team_id = fixture['teams']['home']['id']
    away_team_id = fixture['teams']['away']['id']
    league_id    = fixture['league']['id']
    season       = fixture['league']['season']
 
    # 2. Stats de la saison (buts, victoires, etc.)
    home_season_list = get_json('teams/statistics', {'team': home_team_id, 'league': league_id, 'season': season})
    away_season_list = get_json('teams/statistics', {'team': away_team_id, 'league': league_id, 'season': season})
    home_season = home_season_list[0] if home_season_list else {}
    away_season = away_season_list[0] if away_season_list else {}
 
    # 3. Forme récente (5 derniers matchs terminés)
    home_last5 = get_json('fixtures', {'team': home_team_id, 'last': 5, 'status': 'FT'})
    away_last5 = get_json('fixtures', {'team': away_team_id, 'last': 5, 'status': 'FT'})
 
    def calc_forme(last5, team_id):
        forme = []
        for m in last5:
            home_id    = m['teams']['home']['id']
            home_goals = m['goals']['home'] or 0
            away_goals = m['goals']['away'] or 0
            if team_id == home_id:
                forme.append('W' if home_goals > away_goals else ('D' if home_goals == away_goals else 'L'))
            else:
                forme.append('W' if away_goals > home_goals else ('D' if away_goals == home_goals else 'L'))
        return forme
 
    home_forme = calc_forme(home_last5, home_team_id)
    away_forme = calc_forme(away_last5, away_team_id)
 
    # 4. Cotes
    odds_raw = get_json('odds', {'fixture': fixture_id, 'bet': 1})
    cotes = {'home': None, 'draw': None, 'away': None}
    if odds_raw:
        try:
            values = odds_raw[0]['bookmakers'][0]['bets'][0]['values']
            for v in values:
                if v['value'] == 'Home':   cotes['home'] = v['odd']
                elif v['value'] == 'Draw': cotes['draw'] = v['odd']
                elif v['value'] == 'Away': cotes['away'] = v['odd']
        except:
            pass
 
    # 5. Indice de confiance
    def calc_indice(season_stats, forme, cote):
        score = 50
        for r in forme:
            if r == 'W': score += 6
            elif r == 'D': score += 1
            elif r == 'L': score -= 3
        try:
            buts_m = float(season_stats.get('goals', {}).get('for', {}).get('average', {}).get('total', 0) or 0)
            buts_e = float(season_stats.get('goals', {}).get('against', {}).get('average', {}).get('total', 0) or 0)
            score += (buts_m - buts_e) * 5
        except:
            pass
        try:
            if cote:
                c = float(cote)
                if c < 1.5: score += 10
                elif c < 2.0: score += 5
                elif c > 3.0: score -= 5
        except:
            pass
        return max(5, min(95, int(score)))
 
    home_indice = calc_indice(home_season, home_forme, cotes['home'])
    away_indice = calc_indice(away_season, away_forme, cotes['away'])
 
    # 6. Stats live (si match en cours ou terminé)
    live_stats = {}
    lineups    = []
    events     = []
    status = fixture.get('fixture', {}).get('status', {}).get('short', 'NS')
 
    if status not in ['NS', 'TBD', 'CANC', 'PST']:
        stats_raw = get_json('fixtures/statistics', {'fixture': fixture_id})
        for team_stats in stats_raw:
            team_name = team_stats['team']['name']
            live_stats[team_name] = {s['type']: s['value'] for s in team_stats['statistics']}
        lineups = get_json('fixtures/lineups', {'fixture': fixture_id})
        events  = get_json('fixtures/events',  {'fixture': fixture_id})
 
    return render_template(
        'match.html',
        fixture=fixture,
        home_season=home_season,
        away_season=away_season,
        home_forme=home_forme,
        away_forme=away_forme,
        cotes=cotes,
        home_indice=home_indice,
        away_indice=away_indice,
        live_stats=live_stats,
        lineups=lineups,
        events=events,
        status=status
    )
 
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)