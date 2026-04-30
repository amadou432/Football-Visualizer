import os
import random
from dotenv import load_dotenv
from supabase import create_client

# Charge explicitement le fichier .env
load_dotenv()

# Récupération des variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Vérification de sécurité pour éviter l'erreur "url is required"
if not url or not key:
    print("❌ Erreur : Impossible de lire SUPABASE_URL ou SUPABASE_KEY dans le fichier .env")
    print("Vérifie que ton fichier .env contient bien ces lignes sans espaces autour du '='")
else:
    supabase = create_client(url, key)

    def generer_stats_complexes():
        """Génère des données de test pour la forme et les buts"""
        options = ["W", "D", "L"]
        return {
            "forme_actuelle": {
                "home": [random.choice(options) for _ in range(5)],
                "away": [random.choice(options) for _ in range(5)]
            },
            "moments_buts": {
                "0-15": random.randint(0, 2),
                "16-30": random.randint(0, 3),
                "31-45": random.randint(0, 2),
                "46-60": random.randint(0, 4),
                "61-75": random.randint(0, 2),
                "76-90": random.randint(0, 5)
            },
            "derniere_maj": "2026-04-30"
        }

    def remplir_toute_la_base():
        print("🔍 Récupération de la liste des matchs...")
        # On récupère tous les IDs de la table matchs
        matchs = supabase.table("matchs").select("id").execute()
        
        total = len(matchs.data)
        print(f"🚀 Début du stockage pour {total} matchs.")

        for i, m in enumerate(matchs.data):
            match_id = m['id']
            stats = generer_stats_complexes()
            
            try:
                supabase.table("matchs").update({
                    "details_match": stats
                }).eq("id", match_id).execute()
                
                if i % 10 == 0: # Affiche un message tous les 10 matchs pour suivre l'avancée
                    print(f"⏳ Progression : {i}/{total} matchs remplis...")
            except Exception as e:
                print(f"❌ Erreur sur le match {match_id}: {e}")

        print(f"✅ Terminé ! {total} matchs ont été mis à jour avec des données complexes.")

    if __name__ == "__main__":
        remplir_toute_la_base()