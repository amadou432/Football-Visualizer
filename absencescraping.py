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
 
NOMS_TM_VERS_BDD = {
    # Premier League
    "Arsenal FC":                   "Arsenal",
    "FC Liverpool":                 "Liverpool FC",
    "Manchester City FC":           "Manchester City",
    "Manchester United FC":         "Manchester United",
    "Tottenham Hotspur":         "Tottenham Hotspur FC",
    "Chelsea FC":                   "Chelsea",
    "Newcastle United":          "Newcastle United FC",
    "West Ham United":           "West Ham",
    "Brighton & Hove Albion":    "Brighton",
    "Crystal Palace FC":            "Crystal Palace",
    "FC Brentford":                 "Brentford",
    "FC Fulham":                    "Fulham FC",
    "Wolverhampton Wanderers":   "Wolverhampton Wanderers FC",
    "FC Everton":                   "Everton",
    "Aston Villa":               "Aston Villa FC",
    "Nottingham Forest":            "Nottingham Forest FC",
    "Bournemouth":                  "Bournemouth",
    "Leicester City":               "Leicester",
    "Southampton FC":               "Southampton",
    "AFC Sunderland":               "Sunderland AFC",
    "AFC Bournemouth":              "Bournemouth",


    # Ligue 1
    "Paris Saint-Germain":          "Olympique de Marseille",
    "Marseille":                    "Olympique de Marseille",
    "Lyon":                         "Olympique Lyonnais",
    "AS Monaco":                    "Monaco",
    "OGC Nice":                     "Nice",
    "RC Lens":                      "Lens",
    "Montpellier HSC":              "Montpellier",
    "FC Nantes":                    "Nantes",
    "Strasbourg":         "Strasbourg",
    "Toulouse FC":                  "Toulouse",
    "Stade de Reims":               "Reims",
    "Le Havre AC":                  "Le Havre",
    "AS Saint-Étienne":             "Saint-Etienne",
    "AJ Auxerre":                   "AJ Auxerre",
    "FC Metz":                      "FC Metz",
    "FC Lorient":                   "FC Lorient",
    "Angers SCO":                   "Angers SCO",
    "Stade Brestois 29":            "Stade Brestois 29",
    "RC Lens":                      "Lens",
    # La Liga
    "Atlético de Madrid":           "Club Atlético de Madrid",
    "FC Barcelone":                 "FC Barcelona",
    "Real Madrid CF":               "Real Madrid CF",
    "Athletic Bilbao":                "Athletic Club",
    "CA Osasuna":                   "CA Osasuna",
    "Espanyol Barcelona":            "RCD Espanyol de Barcelona",
    "Getafe CF":                    "Getafe CF",
    "Rayo Vallecano":               "Rayo Vallecano de Madrid",
    "Deportivo Alavés":             "Alaves",
    "RCD Mallorca":                 "RCD Mallorca",
    "Levante UD":                   "Levante UD",
    "Real Sociedad":                "Real Sociedad de Fútbol",
    "Villarreal ":                "Villarreal CF",
    "Real Betis":                   "Real Betis Balompié",
    "Celta Vigo":                   "Celta Vigo",
    "FC Valencia":                  "Valencia CF",
    "Girona FC":                    "Girona",
    # Serie A
    "SSC Napoli":                   "SSC Napoli",
    "Inter Milan":     "FC Internazionale Milano",
    "Juventus Turin":                  "Juventus FC",
    "Lazio Rome":                     "SS Lazio",
    "AS Roma":                      "AS Roma",
    "AC Milan":                     "AC Milan",
    "Atalanta BC":                  "Atalanta",
    "ACF Fiorentina":               "Fiorentina",
    "Torino FC":                    "Torino",
    "Udinese Calcio":               "Udinese Calcio",
    "Genoa CFC":                    "Genoa CFC",
    "Parma Calcio 1913":            "Parma Calcio 1913",
    "FC Bologna":              "Bologna FC 1909",
    "Cagliari Calcio":              "Cagliari",
    "Hellas Verona FC":             "Verona",
    "Empoli FC":                    "Empoli",
    "Venezia FC":                   "Venezia",
    "Como 1907":                    "Como",
    "US Sassuolo":                "Sassuolo",
    # Bundesliga
    "Bayern Munich":            "FC Bayern München",
    "Borussia Dortmund":            "Borussia Dortmund",
    "Bayer 04 Leverkusen":          "Bayer 04 Leverkusen",
    "RB Leipzig":                   "RB Leipzig",
    "VfB Stuttgart":                "VfB Stuttgart",
    "Eintracht Francfort":          "Eintracht Frankfurt",
    "VfL Wolfsburg":                "VfL Wolfsburg",
    "SC Fribourg":                  "SC Freiburg",
    "SV Werder Brême":             "SV Werder Bremen",
    "Borussia Mönchengladbach":     "Borussia Mönchengladbach",
    "FC Augsburg":                  "FC Augsburg",
    "TSG 1899 Hoffenheim":          "TSG 1899 Hoffenheim",
    "1.FC Köln":                   "1. FC Köln",
    "1.FC Union Berlin":           "1. FC Union Berlin",
    "1.FSV Mainz 05":              "1. FSV Mainz 05",
    "FC St. Pauli":                 "FC St. Pauli 1910",
    "FC St. Pauli 1910":            "FC St. Pauli 1910",
    "Hamburger SV":                 "Hamburger SV",
    "1.FC Heidenheim 1846":        "1. FC Heidenheim 1846",
}
 
mois = {
    "janv.": "01", "févr.": "02", "mars": "03",
    "avr.": "04", "mai": "05", "juin": "06",
    "juil.": "07", "août": "08", "sept.": "09",
    "oct.": "10", "nov.": "11", "déc.": "12"
}
 
aujourd_hui = datetime.now()
date_du_jour = aujourd_hui.strftime('%Y-%m-%d')
 
print(f"--- Scraping absents du {date_du_jour} ---")
 
# --- ÉTAPE 1 : Charger TOUTES les équipes de la BDD ---
print("Chargement des équipes depuis Supabase...")
equipes_bdd = {}
for offset in [0, 1000]:# Supabase limite les réponses à 1000 lignes maximum par requête pour ne pas ramer.
                             # On fait donc une boucle en deux voyages : 
                              # - Tour 1 (offset 0) : on prend les 1000 premières équipes
                               # - Tour 2 (offset 1000) : on saute les 1000 premières et on prend les suivantes (1001 à 2000)
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/equipe?select=id_equipe,nom_equipe&offset={offset}&limit=1000",
        headers=HEADERS_SUPA
    ).json()
    for e in res:
        equipes_bdd[e["nom_equipe"]] = e["id_equipe"]
print(f"{len(equipes_bdd)} équipes chargées")
 
# --- ÉTAPE 2 : Vider la table absent (repart à zéro) ---
print("Vidage de la table absent...")
requests.delete(
    f"{SUPABASE_URL}/rest/v1/absent?id_absent=gte.0",
    headers=HEADERS_SUPA
)
 
# --- ÉTAPE 3 : Scraper TOUS les absents des 5 championnats ---
print("\n--- SCRAPING TRANSFERMARKT ---")
absents_par_equipe = {}
 
for league_id, url_tm in CHAMPIONNATS_TM.items():
    print(f"Scraping championnat {league_id}...")
    response_tm = requests.get(url_tm, headers=headers_tm)
    soup = BeautifulSoup(response_tm.text, 'html.parser')
    lignes = soup.find_all("tr", class_=["odd", "even"])
 
    for ligne in lignes:
        nom_td = ligne.find("td", class_="hauptlink")
        if not nom_td:
            continue
        nom = nom_td.text.strip()

        #Récupération de l'image
        img_tag = ligne.find("img", class_="bilderrahmen-fixed")
        # Sécurité : on vérifie si img_tag existe avant de faire .get()
        if img_tag:
            url_photo = img_tag.get("data-src") or img_tag.get("src")
        else:
            url_photo = None
        
 
        logo_club = ligne.find("img", class_="tiny_wappen")
        club_tm = logo_club["alt"] if logo_club else "Inconnu"
 
        # Normalisation du nom
        club = NOMS_TM_VERS_BDD.get(club_tm, club_tm)
 
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
 
        # PLUS DE FILTRE — on garde tous les absents
        if absent:
            if club not in absents_par_equipe:
                absents_par_equipe[club] = []
            absents_par_equipe[club].append({
                "nom": nom,
                "date": date_affichee,
                "photo": url_photo
            })
 
# --- ÉTAPE 4 : Enregistrement dans Supabase ---
print("\n--- ENREGISTREMENT DANS SUPABASE ---")
total = 0
non_trouves = set()
 
for club, joueurs in absents_par_equipe.items():
    id_equipe = equipes_bdd.get(club)
 
    if not id_equipe:
        non_trouves.add(club)
        continue
 
    for joueur in joueurs:
        payload = {
            "nom_joueur": joueur["nom"],
            "date_retour": joueur["date"],
            "id_equipe": id_equipe,
            "photo_joueur": joueur["photo"]
        }
        post_res = requests.post(
            f"{SUPABASE_URL}/rest/v1/absent",
            headers=HEADERS_SUPA,
            json=payload
        )
        if post_res.status_code == 201:
            total += 1
            print(f" {joueur['nom']} ({club})")
        else:
            print(f" Erreur {joueur['nom']} : {post_res.status_code} — {post_res.text}")
 
print(f"\n {total} absents (avec photos) enregistrés au total")
 
if non_trouves:
    print(f"\n Clubs TM non trouvés dans la BDD :")
    for c in sorted(non_trouves):
        print(f"   - '{c}'")