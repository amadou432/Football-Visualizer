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
        "id_equipe, date, buts_marques, buts_encaisses, resultat, domicile, adversaire, nom_equipe, id_match"
    ).execute()
    return forme.data
 
 
def recup_ratio_but_min():
    ratio = supabase.table("ratio_but_min").select(
        "id, id_equipe, "
        "joueur_1_nom, joueur_1_buts, joueur_1_minutes, joueur_1_ratio, joueur_1_photo, "
        "joueur_2_nom, joueur_2_buts, joueur_2_minutes, joueur_2_ratio, joueur_2_photo, "
        "joueur_3_nom, joueur_3_buts, joueur_3_minutes, joueur_3_ratio, joueur_3_photo"
    ).execute()
    return ratio.data

def recup_compo():
    compo = supabase.table("composition").select("id_compo, id_match, nom_joueur, nom_equipe, poste").execute()
    return compo.data

@app.route('/')
def afficher_matchs_bdd():
    match_bdd = []
    equipes = []
    cote = []
 
    try:
        response = supabase.table("match").select(
            "id_match, date_match, heure, nom_champi, id_equipe_dom, id_equipe_ext"
        ).execute()
 
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
    ratio_dom = None
    ratio_ext = None
   
 
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
            ratio_but_min = recup_ratio_but_min()
 
            match['equipe_dom'] = equipes.get(match['id_equipe_dom'], {})
            match['equipe_ext'] = equipes.get(match['id_equipe_ext'], {})
            match['cote'] = cotes_par_match.get(match['id_match'], {})
 
            match['forme_dom'] = [f for f in forme if f['id_equipe'] == match['id_equipe_dom']][-5:]
            match['forme_ext'] = [f for f in forme if f['id_equipe'] == match['id_equipe_ext']][-5:]

 
            absents_dom = [a for a in absent if a['id_equipe'] == match['id_equipe_dom']]
            absents_ext = [a for a in absent if a['id_equipe'] == match['id_equipe_ext']]

            match["date_match"] = match["date_match"]

            
            ratio_but_min = recup_ratio_but_min()
            ratio_dom = next((r for r in ratio_but_min if r['id_equipe'] == match['id_equipe_dom']), None)
            ratio_ext = next((r for r in ratio_but_min if r['id_equipe'] == match['id_equipe_ext']), None)
            
            
            # --- AJOUT DU CALCUL RATIO 90 MIN ---
            def calculer_ratio_90(ratio_obj):
                if ratio_obj:
                    # On calcule pour les 3 joueurs (joueur_1, joueur_2, joueur_3)
                    for i in range(1, 4):
                        buts = ratio_obj.get(f'joueur_{i}_buts', 0)
                        minutes = ratio_obj.get(f'joueur_{i}_minutes', 0)
                        if minutes and minutes > 0:
                            ratio_obj[f'joueur_{i}_ratio_90'] = round((buts / minutes) * 90, 2)
                        else:
                            ratio_obj[f'joueur_{i}_ratio_90'] = 0
                return ratio_obj

            ratio_dom = calculer_ratio_90(ratio_dom)
            ratio_ext = calculer_ratio_90(ratio_ext)
            # ------------------------------------
 
    except Exception as e:
        print(f"Erreur : {e}")
        match = None
 
    
    return render_template("match.html",
                           match=match,
                           forme=forme,
                           absents_dom=absents_dom,
                           absents_ext=absents_ext,
                           ratio_dom=ratio_dom,
                           ratio_ext=ratio_ext)
 
 
if __name__ == '__main__':
    app.run(debug=True, port=5001)