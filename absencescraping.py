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
    39:  "https://www.transfermarkt.fr/premier-league/verletztespieler/wettbewerb/GB1",
    61:  "https://www.transfermarkt.fr/ligue-1/verletztespieler/wettbewerb/FR1",
    140: "https://www.transfermarkt.fr/laliga/verletztespieler/wettbewerb/ES1",
    135: "https://www.transfermarkt.fr/serie-a/verletztespieler/wettbewerb/IT1",
    78:  "https://www.transfermarkt.fr/bundesliga/verletztespieler/wettbewerb/L1"
}
 
headers_tm = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
 
NOMS_TM_VERS_BDD = {
    # Premier League (noms exacts BDD)
    "Arsenal FC":                "Arsenal FC",
    "FC Liverpool":              "Liverpool FC",
    "Manchester City":        "Manchester City FC",
    "Manchester United":      "Manchester United FC",
    "Tottenham Hotspur": "Tottenham Hotspur FC",
    "Chelsea FC":                "Chelsea FC",
    "Newcastle United":          "Newcastle United FC",
    "West Ham United":           "West Ham United FC",
    "Crystal Palace":         "Crystal Palace FC",
    "FC Brentford":              "Brentford FC",
    "FC Fulham":                 "Fulham FC",
    "Wolverhampton Wanderers":   "Wolverhampton Wanderers FC",
    "FC Everton":                "Everton FC",
    "Aston Villa":               "Aston Villa FC",
    "Nottingham Forest":         "Nottingham Forest FC",
    "Bournemouth":               "Bournemouth",
    "AFC Bournemouth":           "AFC Bournemouth",
    "Leicester City":            "Leicester City",
    "Southampton FC":            "Southampton FC",
    "Ipswich Town":              "Ipswich Town",
    "AFC Sunderland":            "Sunderland AFC",
    "Leeds United":            "Leeds United FC",
    "Brighton & Hove Albion":            "Brighton & Hove Albion FC",
 
    # Ligue 1 (noms exacts BDD)
    "Paris Saint-Germain":       "Paris Saint Germain",  # sans tiret dans BDD
    "Marseille":                 "Olympique de Marseille",
    "Lyon":                      "Olympique Lyonnais",
    "AS Monaco":                 "AS Monaco",
    "OGC Nice":                  "Nice",
    "RC Lens":                   "Lens",
    "LOSC Lille":                "Lille OSC",
    "Montpellier HSC":           "Montpellier HSC",
    "FC Nantes":                 "FC Nantes",
    "Strasbourg":                "Strasbourg",
    "Toulouse FC":               "Toulouse FC",
    "Stade de Reims":            "Reims",
    "Le Havre AC":               "Le Havre",
    "AS Saint-Étienne":          "Saint-Etienne",
    "AJ Auxerre":                "AJ Auxerre",
    "FC Lorient":                "FC Lorient",
    "Angers SCO":                "Angers SCO",
    "Stade Brestois 29":         "Stade Brestois 29",
 
    # La Liga (noms exacts BDD)
    "Atlético de Madrid":        "Club Atlético de Madrid",
    "FC Barcelone":              "FC Barcelona",
    "Real Madrid":            "Real Madrid CF",
    "Athletic Bilbao":           "Athletic Club",
    "CA Osasuna":                "CA Osasuna",
    "Espanyol Barcelona":        "RCD Espanyol de Barcelona",
    "Getafe CF":                 "FC Getafe",
    "Rayo Vallecano":            "Rayo Vallecano de Madrid",
    "Deportivo Alavés":          "Deportivo Alavés",
    "RCD Mallorca":              "RCD Mallorca",
    "Real Sociedad":             "Real Sociedad de Fútbol",
    "Villarreal CF":             "Villarreal CF",
    "Villarreal ":               "Villarreal CF",
    "Real Betis":                "Real Betis Balompié",
    "Celta Vigo":                "RC Celta de Vigo",
    "FC Valencia":               "Valencia CF",
    "Girona FC":                 "Girona FC",
    "Séville FC": "Sevilla FC",
    "UD Las Palmas":             "Las Palmas",
    "Las Palmas":                "Las Palmas",
    "Real Valladolid":           "Real Valladolid",
    "Valladolid":                "Real Valladolid",
    "CD Leganés":                "CD Leganés",
    "Elche CF":                "Elche CF",
    "Real Oviedo":                "Real Oviedo",
    "UD Levante":                "Levante UD",

 
    # Serie A (noms exacts BDD)
    "SSC Napoli":                "SSC Napoli",
    "Inter Milan":               "Inter Milan",
    "Juventus Turin":            "Juventus FC",
    "Lazio Rome":                "SS Lazio",
    "AS Roma":                   "AS Roma",
    "AC Milan":                  "AC Milan",
    "Atalanta BC":               "Atalanta",
    "ACF Fiorentina":            "ACF Fiorentina",
    "Torino FC":                 "Torino FC",
    "Udinese Calcio":            "Udinese Calcio",
    "Genoa CFC":                 "Genoa CFC",
    "Parma Calcio 1913":         "Parma Calcio 1913",
    "FC Bologna":                "Bologna FC 1909",
    "Cagliari Calcio":           "Cagliari Calcio",
    "Hellas Verona":          "Hellas Verona FC",
    "Empoli FC":                 "Empoli",
    "Venezia FC":                "Venezia FC",
    "Como 1907":                 "Como 1907",
    "AC Monza":                  "Monza",
    "Monza":                     "Monza",
    "US Lecce":                  "US Lecce",
    "Lecce":                     "Lecce",
    "US Sassuolo":                     "US Sassuolo Calcio",
    "Inter Milan":                     "FC Internazionale Milano",
     "Atalanta BC":                     "Atalanta BC",
      "Pisa Sporting Club":                     "AC Pisa 1909",

 
    # Bundesliga
    "Bayern Munich":             "FC Bayern München",
    "Borussia Dortmund":         "Borussia Dortmund",
    "Bayer 04 Leverkusen":       "Bayer 04 Leverkusen",
    "RB Leipzig":                "RB Leipzig",
    "VfB Stuttgart":             "VfB Stuttgart",
    "Eintracht Francfort":       "Eintracht Frankfurt",
    "VfL Wolfsburg":             "VfL Wolfsburg",
    "SC Fribourg":               "SC Freiburg",
    "SV Werder Brême":           "SV Werder Bremen",
    "Borussia Mönchengladbach":  "Borussia Mönchengladbach",
    "FC Augsburg":               "FC Augsburg",
    "TSG 1899 Hoffenheim":       "TSG 1899 Hoffenheim",
    "1.FC Köln":                 "1. FC Köln",
    "1.FC Union Berlin":         "1. FC Union Berlin",
    "1.FSV Mainz 05":            "1. FSV Mainz 05",
    "FC St. Pauli":              "FC St. Pauli 1910",
    "FC St. Pauli 1910":         "FC St. Pauli 1910",
    "Hamburger SV":              "Hamburger SV",
    "1.FC Heidenheim 1846":      "FC Heidenheim",
}
 
mois = {
    "janv.": "01", "févr.": "02", "mars": "03",
    "avr.":  "04", "mai":   "05", "juin": "06",
    "juil.": "07", "août":  "08", "sept.": "09",
    "oct.":  "10", "nov.":  "11", "déc.": "12"
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
 
# --- ÉTAPE 2 : Vider la table absent ---
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
 
        img_tag = ligne.find("img", class_="bilderrahmen-fixed")
        url_photo = (img_tag.get("data-src") or img_tag.get("src")) if img_tag else None
 
        logo_club = ligne.find("img", class_="tiny_wappen")
        club_tm = logo_club["alt"] if logo_club else "Inconnu"
 
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
            "nom_joueur":  joueur["nom"],
            "date_retour": joueur["date"],
            "id_equipe":   id_equipe,
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