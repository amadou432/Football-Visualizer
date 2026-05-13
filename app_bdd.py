from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

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


def recup_absent(match_id):
    res = supabase.table("absent").select("*").eq("id_match", match_id).execute()
    return res.data


@app.route('/')
def afficher_matchs_bdd():
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).execute()
        match_bdd = response.data
        equipes = recup_toutes_equipes()
        cote = recup_cote()

        # FIX : une seule fois, proprement
        cotes_par_match = {c["id_match"]: c for c in cote}
        for m in match_bdd:
            m["cote"] = cotes_par_match.get(m["id_match"], {})

        # Filtrer les matchs qui ont bien les deux équipes
        match_bdd = [m for m in match_bdd if m['id_equipe_dom'] and m['id_equipe_ext']]

    except Exception as e:
        print(f"Erreur : {e}")
        match_bdd = []
        equipes = []
        cote = []

    return render_template("home.html", match=match_bdd, equipe=equipes, cote=cote)


@app.route('/match/<int:id>')
def afficher_match(id):
    match = None
    absents_dom = []
    absents_ext = []
    forme = []

    try:
        # 1. Récupération du match
        response = supabase.table("match").select("*").eq("id_match", id).execute()

        if response.data:
            match = response.data[0]

            # 2. Récupération des équipes
            toutes_equipes = recup_toutes_equipes()
            equipes_map = {e['id_equipe']: e for e in toutes_equipes}

            # 3. Récupération des cotes
            cotes = recup_cote()
            cotes_par_match = {c["id_match"]: c for c in cotes}

            # FIX : on récupère les absents AVANT d'écraser id_equipe_dom/ext
            # car à ce stade ce sont encore des entiers, ce qu'on veut pour filtrer
            absents_data = recup_absents(id)
            absents_dom = [a for a in absents_data if int(a['id_equipe']) == int(match['id_equipe_dom'])]
            absents_ext = [a for a in absents_data if int(a['id_equipe']) == int(match['id_equipe_ext'])]
            print(f"DEBUG - Absents trouvés pour ce match : {absents_data}")
            # 4. Enrichissement du match avec les objets équipe et cote
            match['equipe_dom'] = equipes_map.get(match['id_equipe_dom'], {})
            match['equipe_ext'] = equipes_map.get(match['id_equipe_ext'], {})
            match['cote'] = cotes_par_match.get(match['id_match'], {})

            # 5. Forme des équipes
            forme = recup_forme_equipe()

    except Exception as e:
        print(f"Erreur critique : {e}")

    return render_template("match.html",
                           match=match,
                           forme=forme,
                           absents_dom=absents_dom,
                           absents_ext=absents_ext)


if __name__ == '__main__':
    app.run(debug=True, port=5001)