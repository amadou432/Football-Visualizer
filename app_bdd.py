import os
from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

url = os.getenv("https://deqthaukwlduxbsbmqgz.supabase.co")
key = os.getenv("sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK")
supabase: Client = create_client(url, key)

@app.route('/')
def afficher_matchs_bdd():
    try:
        
        response = supabase.table("matchs").select(
            "id, date, heure, league_name, home_name, home_logo, away_name, away_logo, venue_name"
        ).execute()
        
        matchs_bdd = response.data
        
    except Exception as e:
        print(f"Erreur de connexion Supabase : {e}")
        matchs_bdd = []

    return render_template("affichage.html", matchs=matchs_bdd)

if __name__ == '__main__':
    app.run(debug=True, port=5001)