import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuration Supabase
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
# Ta nouvelle clé doit être dans le .env sous FOOTBALL_API_KEY
API_KEY = os.getenv("FOOTBALL_API_KEY")

def determiner_resultat(buts_equipe, buts_adversaire):
    if buts_equipe is None or buts_adversaire is None: return '?'
    if buts_equipe > buts_adversaire: return 'W'
    if buts_equipe < buts_adversaire: return 'L'
    return 'D'

def maj_derniers_matchs():
    # On change l'URL : on demande les matchs d'une date spécifique en 2024 (autorisé en Free)
    # On teste avec le 19 mai 2024 (dernière journée de PL)
    url = "https://v3.football.api-sports.io/fixtures?league=39&season=2025&date=2026-05-9"
    headers = {'x-apisports-key': API_KEY}

    print(f"⚽️ Tentative sur la date 2024-05-19...")
    response = requests.get(url, headers=headers).json()
    
    errors = response.get('errors')
    if errors:
        print(f"❌ Erreur API : {errors}")
    
    matchs = response.get('response', [])
    print(f"📊 Nombre de matchs récupérés : {len(matchs)}")

    for m in matchs:
        # Équipe Domicile
        home_data = {
            "id_equipe": m['teams']['home']['id'],
            "team_name": m['teams']['home']['name'],
            "match_id": m['fixture']['id'],
            "date": m['fixture']['date'][:10],
            "buts_marques": m['goals']['home'],
            "buts_encaisses": m['goals']['away'],
            "resultat": determiner_resultat(m['goals']['home'], m['goals']['away']),
            "domicile": True,
            "adversaire": m['teams']['away']['name']
        }

        # Équipe Extérieur
        away_data = {
            "id_equipe": m['teams']['away']['id'],
            "team_name": m['teams']['away']['name'],
            "match_id": m['fixture']['id'],
            "date": m['fixture']['date'][:10],
            "buts_marques": m['goals']['away'],
            "buts_encaisses": m['goals']['home'],
            "resultat": determiner_resultat(m['goals']['away'], m['goals']['home']),
            "domicile": False,
            "adversaire": m['teams']['home']['name']
        }

        for data in [home_data, away_data]:
            try:
                res = supabase.table("forme_equipes").insert(data).execute()
                if res.data:
                    print(f"✅ Ajouté : {data['team_name']} ({data['resultat']})")
            except Exception as e:
                # Si le match est déjà là, on ne pollue pas le terminal
                if "duplicate key" in str(e):
                    print(f"ℹ️ {data['team_name']} : Match déjà enregistré.")
                else:
                    print(f"❌ Erreur Supabase pour {data['team_name']} : {e}")

if __name__ == "__main__":
    maj_derniers_matchs()