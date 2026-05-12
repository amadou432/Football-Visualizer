import requests
from datetime import datetime, timedelta # On importe "timedelta" pour calculer les dates futures (aujourd'hui + 9 jours)

# --- CONFIGURATION DES CLÉS ---
API_KEY = "cd1427ada30b4ce08d0b447f29938e76"
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"  # Permet l'UPSERT (mise à jour si doublon)
}

HEADERS_API = {
    "X-Auth-Token": API_KEY
}

# Codes des 5 grands championnats sur Football-Data
LIGUES_CODES = ["PL", "FL1", "PD", "SA", "BL1"]

# Dictionnaire de traduction en français (sans émoji pour la base de données)
TRADUCTION_CHAMPIONNATS = {
    "Premier League": "Premier League",
    "Ligue 1": "Ligue 1",
    "Primera Division": "La Liga",
    "Serie A": "Serie A",
    "Bundesliga": "Bundesliga"
}

# --- PARAMÈTRE DE RECHERCHE (9 JOURS) ---
# Le script récupère aujourd'hui + les 9 prochains jours
NOMBRE_DE_JOURS = 9

date_debut = datetime.now().strftime('%Y-%m-%d')
date_fin = (datetime.now() + timedelta(days=NOMBRE_DE_JOURS)).strftime('%Y-%m-%d')

print("=" * 70)
print(f" Synchro & Insertion BDD : du {date_debut} au {date_fin} ({NOMBRE_DE_JOURS} jours)")
print("=" * 70)

# 1. APPEL À L'API FOOTBALL-DATA
response = requests.get(
    "https://api.football-data.org/v4/matches",
    headers=HEADERS_API,
    params={
        "dateFrom": date_debut,
        "dateTo": date_fin,
        "competitions": ",".join(LIGUES_CODES) #join() sert à coller les éléments d’une liste ensemble.
    }
)

if response.status_code != 200: # Si le status n'est pas 200 (= succès) → on affiche l'erreur
    print(f"Erreur API ({response.status_code}) : {response.text}")
else:
    donnees = response.json()
    matchs_api = donnees.get("matches", [])
    
    print(f"-> {len(matchs_api)} match(s) trouvé(s) sur l'API.\n")

    if not matchs_api:
        print("Aucun match à insérer.")
    else:
        equipes_dict = {}
        liste_matchs = []

        # 2. TRAITEMENT ET PRÉPARATION DES DONNÉES
        for match in matchs_api:
            # Gestion de la date et de l'heure locale (+2h pour l'heure d'été française)
            date_utc = match["utcDate"]   # L'API renvoie la date en UTC ex: "2026-05-12T19:00:00Z"
            date_match = date_utc[:10]    # On prend juste les 10 premiers caractères = "2026-05-12"
            
            try:
                heure_utc = datetime.strptime(date_utc, "%Y-%m-%dT%H:%M:%SZ")  # On convertit le texte en objet datetime Python
                heure_locale = heure_utc + timedelta(hours=2) 
                heure_match_str = heure_locale.strftime("%H:%M")
            except ValueError:
                heure_match_str = date_utc[11:16]

            # Traduction du championnat pour qu'il s'insère proprement
            nom_original = match["competition"]["name"]
            nom_français = TRADUCTION_CHAMPIONNATS.get(nom_original, nom_original)

            # Extraction des équipes (pour éviter les doublons dans le dictionnaire)
            for side in ["homeTeam", "awayTeam"]:
                team = match[side]
                equipes_dict[team["id"]] = {
                    "id_equipe": team["id"],
                    "nom_equipe": team["name"],
                    "logo_equipe": team["crest"]  # 'crest' contient l'URL du logo (blason) sur Football-Data
                }

            # Préparation de l'objet match pour Supabase
            liste_matchs.append({
                "id_match": match["id"],
                "date_match": date_match,
                "heure": heure_match_str,
                "nom_champi": nom_français,
                "id_equipe_dom": match["homeTeam"]["id"],
                "id_equipe_ext": match["awayTeam"]["id"]
            })

        liste_equipes_final = list(equipes_dict.values())

        # 3. ENVOI DES DONNÉES À SUPABASE
        print(f"Envoi de {len(liste_equipes_final)} équipes vers Supabase...")
        res_equipes = requests.post(
            f"{SUPABASE_URL}/rest/v1/equipe",
            headers=HEADERS_SUPA,
            json=liste_equipes_final
        )
        
        if res_equipes.status_code in [200, 201, 204]:
            print("  Mise à jour des équipes réussie !")
        else:
            print(f"  Attention - Problème d'insertion des équipes : {res_equipes.text}")

        print(f"Envoi de {len(liste_matchs)} matchs vers Supabase...")
        res_matchs = requests.post(
            f"{SUPABASE_URL}/rest/v1/match",
            headers=HEADERS_SUPA,
            json=liste_matchs
        )

        if res_matchs.status_code in [200, 201, 204]:
            print(f"  RÉUSSITE ! {len(liste_matchs)} matchs stockés dans ta base Supabase.")
        else:
            print(f"  Erreur lors de l'envoi des matchs : {res_matchs.text}")

print("\n" + "=" * 70)
