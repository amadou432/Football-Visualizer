import requests
from bs4 import BeautifulSoup
from datetime import datetime

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

CHAMPIONNATS_TM = {
    39: "https://www.transfermarkt.fr/premier-league/verletztespieler/wettbewerb/GB1",
    61: "https://www.transfermarkt.fr/ligue-1/verletztespieler/wettbewerb/FR1",
    140: "https://www.transfermarkt.fr/laliga/verletztespieler/wettbewerb/ES1",
    135: "https://www.transfermarkt.fr/serie-a/verletztespieler/wettbewerb/IT1",
    78: "https://www.transfermarkt.fr/bundesliga/verletztespieler/wettbewerb/L1"
}

headers_tm = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

mois = {
    "janv.": "01", "févr.": "02", "mars": "03",
    "avr.": "04", "mai": "05", "juin": "06",
    "juil.": "07", "août": "08", "sept.": "09",
    "oct.": "10", "nov.": "11", "déc.": "12"
}

aujourd_hui = datetime.now()
date_du_jour = aujourd_hui.strftime('%Y-%m-%d')

print(f"--- Matchs du {date_du_jour} ---")

# --- ÉTAPE 1 : Récupérer les matchs depuis Supabase ---
res = requests.get(
    f"{SUPABASE_URL}/rest/v1/match?date_match=eq.{date_du_jour}",
    headers=HEADERS_SUPA
)
matchs = res.json()

# FIX : initialisation anticipée pour éviter les NameError si matchs est vide
absents_par_equipe = {}

if not matchs:
    print("Pas de matchs aujourd'hui dans Supabase")
else:
    print(f"{len(matchs)} matchs trouvés dans Supabase")

    # On récupère les IDs des équipes qui jouent aujourd'hui
    ids_equipes = set()
    for match in matchs:
        ids_equipes.add(match["id_equipe_dom"])
        ids_equipes.add(match["id_equipe_ext"])

    # On récupère les noms des équipes depuis Supabase
    equipes_du_jour = {}
    for id_equipe in ids_equipes:
        res_eq = requests.get(
            f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{id_equipe}",
            headers=HEADERS_SUPA
        )
        equipe = res_eq.json()
        if equipe:
            equipes_du_jour[equipe[0]["nom_equipe"]] = id_equipe

    # --- ÉTAPE 2 : Scrapper les absents sur Transfermarkt ---
    for league_id, url_tm in CHAMPIONNATS_TM.items():
        response_tm = requests.get(url_tm, headers=headers_tm)
        soup = BeautifulSoup(response_tm.text, 'html.parser')
        lignes = soup.find_all("tr", class_=["odd", "even"])

        for ligne in lignes:
            nom_td = ligne.find("td", class_="hauptlink")
            if not nom_td:
                continue
            nom = nom_td.text.strip()

            logo_club = ligne.find("img", class_="tiny_wappen")
            club = logo_club["alt"] if logo_club else "Inconnu"
            

            dates = ligne.find_all("td", class_="zentriert")
            date_retour_texte = dates[-1].text.strip() if dates else ""

            absent = False
            date_affichee = "Pas de date retrouvée"

            if not date_retour_texte:
                absent = True
            else:
                try:
                    texte = date_retour_texte
                    for fr, num in mois.items():
                        texte = texte.replace(fr, num)
                    date_retour = datetime.strptime(texte, "%d %m %Y")
                    if date_retour >= aujourd_hui:
                        absent = True
                        date_affichee = date_retour_texte
                except:
                    absent = True

            if absent and club in equipes_du_jour:
                if club not in absents_par_equipe:
                    absents_par_equipe[club] = []
                absents_par_equipe[club].append({
                    "nom": nom,
                    "date": date_affichee
                })

    # --- ÉTAPE 3 : Affichage par match ---
    print("\n--- ABSENTS PAR MATCH ---")
    for match in matchs:
        res_dom = requests.get(f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{match['id_equipe_dom']}", headers=HEADERS_SUPA).json()
        res_ext = requests.get(f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{match['id_equipe_ext']}", headers=HEADERS_SUPA).json()

        dom = res_dom[0]["nom_equipe"] if res_dom else "Inconnu"
        ext = res_ext[0]["nom_equipe"] if res_ext else "Inconnu"

        print(f"\n{match['nom_champi']} | {dom} vs {ext}")

        for equipe in [dom, ext]:
            absents = absents_par_equipe.get(equipe, [])
            if absents:
                print(f"  Absents {equipe} :")
                for j in absents:
                    print(f"      {j['nom']} — {j['date']}")
            else:
                print(f"  Aucun absent connu pour {equipe}")

    # --- ÉTAPE 4 : Enregistrement dans la base de données ---
    print("\n--- ENREGISTREMENT DANS SUPABASE ---")

    for match in matchs:
        id_m = match['id_match']

        for type_eq in ['dom', 'ext']:
            id_eq = match[f'id_equipe_{type_eq}']

            res_eq = requests.get(
                f"{SUPABASE_URL}/rest/v1/equipe?id_equipe=eq.{id_eq}",
                headers=HEADERS_SUPA
            ).json()
            nom_equipe_bdd = res_eq[0]["nom_equipe"] if res_eq else None

            if nom_equipe_bdd in absents_par_equipe:
                for joueur in absents_par_equipe[nom_equipe_bdd]:

                    # FIX : vérification doublon avant insertion
                    check = requests.get(
                        f"{SUPABASE_URL}/rest/v1/absent?nom_joueur=eq.{joueur['nom']}&id_match=eq.{id_m}",
                        headers=HEADERS_SUPA
                    ).json()

                    if check:
                        print(f"⏩ {joueur['nom']} déjà en base ({nom_equipe_bdd}), ignoré")
                        continue

                    payload = {
                        "nom_joueur": joueur["nom"],
                        "date_retour": joueur["date"],
                        "id_equipe": id_eq,
                        "id_match": id_m
                    }
                    post_res = requests.post(
                        f"{SUPABASE_URL}/rest/v1/absent",
                        headers=HEADERS_SUPA,
                        json=payload
                    )
                    if post_res.status_code == 201:
                        print(f"✅ {joueur['nom']} enregistré ({nom_equipe_bdd})")
                    else:
                        print(f"❌ Erreur pour {joueur['nom']} : {post_res.status_code} — {post_res.text}")