import requests
from datetime import datetime

# CONFIGURATION DIRECTE API-FOOTBALL
API_KEY = "4699e04f58328f5c4e16bad40d5cdb27" 

HEADERS = {
    "x-apisports-key": API_KEY
}

# Les IDs des 5 grands championnats sur API-Football
CHAMPIONNATS = {
    "Premier League (Angleterre)": 39,
    "Ligue 1 (France)": 61,
    "La Liga (Espagne)": 140,
    "Serie A (Italie)": 135,
    "Bundesliga (Allemagne)": 78
}

# Date du jour (2026-05-13)
date_du_jour = datetime.now().strftime('%Y-%m-%d')
# La saison active pour les matchs de mai 2026 est la saison 2025
saison_actuelle = 2025

print(f"--- COMPOSITIONS PROBABLES DU JOUR ({datetime.now().strftime('%d/%m/%Y')}) ---")

for nom_champi, id_champi in CHAMPIONNATS.items():
    
    url = f"https://v3.football.api-sports.io/fixtures?date={date_du_jour}&league={id_champi}&season={saison_actuelle}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Erreur de connexion pour la {nom_champi} (Code {response.status_code})")
            continue
            
        donnees = response.json().get("response", [])
        if not donnees:
            continue
            
        for match in donnees:
            lineups = match.get("lineups", [])
            
            # Si l'API n'a pas encore mis de compositions pour ce match, on passe
            if not lineups:
                continue
                
            eq_dom = match["teams"]["home"]["name"]
            eq_ext = match["teams"]["away"]["name"]
            print(f"\nMatch : {eq_dom} vs {eq_ext}")
            print("-" * 50)
                
            for lineup in lineups:
                nom_equipe = lineup["team"]["name"]
                formation = lineup.get("formation", "N/A")
                
                print(f"   Compo {nom_equipe} ({formation}) :")
                
                titulaires = lineup.get("startXI", [])
                for t in titulaires:
                    nom_joueur = t["player"]["name"]
                    poste = t["player"]["pos"]
                    print(f"      [{poste}] {nom_joueur}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Erreur lors du traitement de la {nom_champi} : {e}")

print("\n--- Fin de la récupération des compositions ---")