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

def recup_cote():
    cote = supabase.table("cote").select(
        "id_cote, cote_1, cote_n, cote_2, id_match, bookmaker_1, bookmaker_n, bookmaker_2"
        ).execute()
    return cote.data

def recup_forme_equipe():
    forme = supabase.table("forme_equipes").select(
        "id_equipe, team_name, match_id, date, buts_marques, buts_encaisses, resultat, domicile, adversaire"
    ).execute()
    return forme.data

@app.route('/')
def afficher_matchs_bdd():
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).gte("date_match", str(date.today())).execute()
        match_bdd = response.data
        equipes = recup_toutes_equipes()
        cote = recup_cote()

        cotes_par_match = {c["id_match"]: c for c in cote}
        for m in match_bdd:
            m["cote"] = cotes_par_match.get(m["id_match"], {})

    except Exception as e:
        print(f"Erreur : {e}")
        match_bdd = []
        equipes = []
        # Filtrer les matchs qui ont bien les deux équipes
        match_bdd = [m for m in match_bdd if m['id_equipe_dom'] and m['id_equipe_ext']]
    print("PREMIER MATCH COTE :", match_bdd[0].get('cote'))
    cotes_par_match = {c["id_match"]: c for c in cote}
    print("NOMBRE COTES :", len(cotes_par_match))
    for m in match_bdd:
        m["cote"] = cotes_par_match.get(m["id_match"], {})
    print("IDS COTES :", list(cotes_par_match.keys())[:5])
    print("IDS MATCHS :", [m["id_match"] for m in match_bdd[:5]])
    return render_template("home.html", match=match_bdd, equipe=equipes, cote=cote)


@app.route('/match/<int:id>')
def afficher_match(id):
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).eq("id_match", id).execute()
        match = response.data[0] if response.data else None

        toutes_equipes = recup_toutes_equipes()
        equipes = {e['id_equipe']: e for e in toutes_equipes}

        cotes = recup_cote()
        cotes_par_match = {c["id_match"]: c for c in cotes}
        forme = recup_forme_equipe()  # ← déjà là

        if match:
            match['equipe_dom'] = equipes.get(match['id_equipe_dom'], {})
            match['equipe_ext'] = equipes.get(match['id_equipe_ext'], {})
            match['cote'] = cotes_par_match.get(match['id_match'], {})
            
            forme_dom = [f for f in forme if f['id_equipe'] == match['id_equipe_dom']][-5:]
            forme_ext = [f for f in forme if f['id_equipe'] == match['id_equipe_ext']][-5:]
            
            match['forme_dom'] = forme_dom
            match['forme_ext'] = forme_ext
            print("FORME DOM :", match['forme_dom'])
            print("FORME EXT :", match['forme_ext'])
            print("ID EQUIPE DOM :", match['id_equipe_dom'])

    except Exception as e:
        print(f"Erreur : {e}")
        match = None
        forme = []  # ← ajoute ça

    return render_template("match.html", match=match, forme=forme)
if __name__ == '__main__':
    app.run(debug=True, port=5001)