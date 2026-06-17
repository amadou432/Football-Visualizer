import requests
import time

# ============================================================
# CONFIGURATION DES API
# ============================================================
FOOTBALL_API_KEY = "cd1427ada30b4ce08d0b447f29938e76"
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_FD = {"X-Auth-Token": FOOTBALL_API_KEY}
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Dictionnaire des 5 grands championnats avec leur code API officiel
CHAMPIONNATS = {
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
}

# ============================================================
# FONCTIONS DE NAVIGATION ET REQUÊTES
# ============================================================

def obtenir_classement_api(code_championnat):
    """Récupère le tableau de classement trié depuis l'API Football-Data"""
    url = f"https://api.football-data.org/v4/competitions/{code_championnat}/standings?season=2025"
    try:
        res = requests.get(url, headers=HEADERS_FD, timeout=15)
        if res.status_code == 200:
            standings = res.json().get("standings", [])
            # On extrait le classement général appelé 'TOTAL'
            for st in standings:
                if st.get("type") == "TOTAL":
                    return st.get("table", [])
        else:
            print(f" Erreur API Football-Data ({res.status_code}) : {res.text}")
        return []
    except Exception as e:
        print(f" Exception lors de l'appel API : {e}")
        return []

def inserer_classement_supabase(liste_lignes):
    """Insère un lot de lignes de classement directement dans Supabase"""
    if not liste_lignes:
        return
    url = f"{SUPABASE_URL}/rest/v1/classement"
    try:
        res = requests.post(url, headers=HEADERS_SUPA, json=liste_lignes)
        if res.status_code in [200, 201, 204]:
            print(f"    {len(liste_lignes)} équipes enregistrées en BDD.")
        else:
            print(f"    Erreur insertion Supabase ({res.status_code}) : {res.text}")
    except Exception as e:
        print(f"    Erreur envoi BDD : {e}")

# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("=== REMPLISSAGE DE LA TABLE CLASSEMENT ===\n")

    total_lignes_inserees = 0

    # Boucle sur chacun des 5 championnats
    for nom_champi, code in CHAMPIONNATS.items():
        print(f"\n Récupération du classement : {nom_champi} ({code})...")
        table_classement = obtenir_classement_api(code)
        
        payload_classement = []
        
        for ligne in table_classement:
            id_club_api = ligne["team"]["id"] # L'ID qui correspond à ta table equipe
            nom_club_api = ligne["team"]["name"]
            
            # Préparation de la ligne à insérer
            payload_classement.append({
                "position": ligne["position"],
                "id_equipe": id_club_api, # Clé étrangère connectée à 'equipe'
                "nom_champi": nom_champi,
                "points": ligne["points"],
                "matchs_joues": ligne["playedGames"],
                "diff_buts": ligne["goalDifference"]
            })
            
        # Envoi des données du championnat actuel sur Supabase
        if payload_classement:
            inserer_classement_supabase(payload_classement)
            total_lignes_inserees += len(payload_classement)
        else:
            print(f"    Aucun classement récupéré pour la compétition {nom_champi}.")
        
        # Pause de 6 secondes pour respecter les quotas de l'API gratuite
        print("    Temporisation de 6 secondes avant le prochain championnat...")
        time.sleep(6)

    print(f"\n=== FIN DE SCRIPT — {total_lignes_inserees} lignes insérées dans la table ! ===")