from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import date
 
load_dotenv()
 
app = Flask(__name__)
 
url = "https://deqthaukwlduxbsbmqgz.supabase.co"
key = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"
supabase: Client = create_client(url, key)
 
 
def recup_toutes_equipes():
    equipes1 = supabase.table("equipe").select(
        "id_equipe, nom_equipe, logo_equipe"
    ).range(0, 999).execute()
    equipes2 = supabase.table("equipe").select(
        "id_equipe, nom_equipe, logo_equipe"
    ).range(1000, 1999).execute()
    return equipes1.data + equipes2.data
 
 
def recup_absent():
    absent = supabase.table("absent").select(
        "nom_joueur, id_equipe, date_retour, photo_joueur"
    ).execute()
    return absent.data
 
 
def recup_cote():
    cote = supabase.table("cote").select(
        "id_cote, cote_1, cote_n, cote_2, id_match, bookmaker_1, bookmaker_n, bookmaker_2"
    ).execute()
    return cote.data
 
 
def recup_forme_equipe():
    forme = supabase.table("forme_equipes").select(
        "id_equipe, team_name, match_id, date, buts_marques, buts_encaisses, domicile, adversaire"
    ).execute()
    return forme.data
 
 
@app.route('/')
def afficher_matchs_bdd():
    match_bdd = []
    equipes = []
    cote = []
 
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).gte("date_match", str(date.today())).execute()
 
        match_bdd = response.data
        equipes = recup_toutes_equipes()
        cote = recup_cote()
 
        # FIX : tout dans le try, une seule fois
        match_bdd = [m for m in match_bdd if m['id_equipe_dom'] and m['id_equipe_ext']]
        cotes_par_match = {c["id_match"]: c for c in cote}
        for m in match_bdd:
            m["cote"] = cotes_par_match.get(m["id_match"], {})
 
    except Exception as e:
        print(f"Erreur : {e}")
 
    return render_template("home.html", match=match_bdd, equipe=equipes, cote=cote)
 
 
@app.route('/match/<int:id>')
def afficher_match(id):
    match = None
    forme = []
    absents_dom = []
    absents_ext = []
 
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).eq("id_match", id).execute()
 
        match = response.data[0] if response.data else None
 
        if match:
            toutes_equipes = recup_toutes_equipes()
            equipes = {e['id_equipe']: e for e in toutes_equipes}
 
            cotes = recup_cote()
            cotes_par_match = {c["id_match"]: c for c in cotes}
 
            forme = recup_forme_equipe()
            absent = recup_absent()
 
            match['equipe_dom'] = equipes.get(match['id_equipe_dom'], {})
            match['equipe_ext'] = equipes.get(match['id_equipe_ext'], {})
            match['cote'] = cotes_par_match.get(match['id_match'], {})
 
            match['forme_dom'] = [f for f in forme if f['id_equipe'] == match['id_equipe_dom']][-5:]
            match['forme_ext'] = [f for f in forme if f['id_equipe'] == match['id_equipe_ext']][-5:]
 
            # FIX : variables séparées pour le template
            absents_dom = [a for a in absent if a['id_equipe'] == match['id_equipe_dom']]
            absents_ext = [a for a in absent if a['id_equipe'] == match['id_equipe_ext']]
 
    except Exception as e:
        print(f"Erreur : {e}")
        match = None
 
    if match is None:
        return render_template("erreur.html", message=f"Match {id} introuvable."), 404
 
    return render_template("match.html",
                           match=match,
                           forme=forme,
                           absents_dom=absents_dom,
                           absents_ext=absents_ext)
 
 
if __name__ == '__main__':
    app.run(debug=True, port=5001)