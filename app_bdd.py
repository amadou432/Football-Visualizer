import os
from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Tes identifiants Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") # Utilise l'env pour la sécurité
supabase: Client = create_client(url, key)

@app.route('/')
def afficher_matchs_bdd():
    try:
        # Récupération simplifiée pour la page d'accueil
        response = supabase.table("matchs").select(
            "id, date, heure, league_name, home_name, home_logo, away_name, away_logo, venue_name"
        ).execute()
        matchs_bdd = response.data
    except Exception as e:
        print(f"Erreur Supabase (Home) : {e}")
        matchs_bdd = []
    return render_template("home.html", matchs=matchs_bdd)


@app.route('/match/<int:id>')
def afficher_match(id):
    try:
        # RÉCUPÉRATION DE TOUTES LES DONNÉES (y compris details_match !)
        # On utilise .single() car on veut un seul objet, pas une liste
        response = supabase.table("matchs").select("*").eq("id", id).single().execute()
        match_data = response.data
        
        if not match_data:
            return "Match non trouvé", 404

    except Exception as e:
        print(f"Erreur Supabase (Details) : {e}")
        return "Erreur lors du chargement des détails", 500

    # On envoie match_data au template sous le nom 'match'
    return render_template("match.html", match=match_data)

if __name__ == '__main__':
    # Lance le serveur sur le port 5001 comme tu l'as configuré
    app.run(debug=True, port=5001)