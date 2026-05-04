import os
from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

url = "https://deqthaukwlduxbsbmqgz.supabase.co"
key = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"
supabase: Client = create_client(url, key)

@app.route('/')
def afficher_matchs_bdd():
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).execute()
        match_bdd = response.data

        equipes_response = supabase.table("equipe").select(
            "id_equipe, nom_equipe, logo_equipe"
        ).execute()
        equipes = equipes_response.data

    except Exception as e:
        print(f"Erreur : {e}")
        match_bdd = []
        equipes = []

    return render_template("home.html", match=match_bdd, equipe=equipes)


@app.route('/match/<int:id>')
def afficher_match(id):
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).eq("id_match", id).execute()
        match = response.data[0] if response.data else None

        equipes_response = supabase.table("equipe").select(
            "id_equipe, nom_equipe, logo_equipe"
        ).execute()
        equipes = {e['id_equipe']: e for e in equipes_response.data}

        if match:
            match['equipe_dom'] = equipes.get(match['id_equipe_dom'], {})
            match['equipe_ext'] = equipes.get(match['id_equipe_ext'], {})

    except Exception as e:
        print(f"Erreur : {e}")
        match = None

    return render_template("match.html", match=match)

if __name__ == '__main__':
    app.run(debug=True, port=5001)