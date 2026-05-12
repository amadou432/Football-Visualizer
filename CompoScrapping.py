import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

headers_web = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

date_du_jour = datetime.now().strftime('%Y-%m-%d')
print(f"--- ⚽ COMPOS PROBABLES DU {datetime.now().strftime('%d/%m/%Y')} ---")

# --- ÉTAPE 1 : Récupérer TOUTES les équipes de la BDD d'un coup (Plus de bugs d'IDs) ---
print("📦 Chargement des équipes depuis Supabase...")
res_eq = requests.get(f"{SUPABASE_URL}/rest/v1/equipe?limit=5000", headers=HEADERS_SUPA)
if res_eq.status_code == 200:
    equipes_bdd = {e["id_equipe"]: e["nom_equipe"] for e in res_eq.json()}
    print(f"✅ {len(equipes_bdd)} équipes chargées en mémoire.")
else:
    equipes_bdd = {}
    print("⚠️ Impossible de charger les équipes depuis Supabase.")

# --- ÉTAPE 2 : Récupérer tes matchs du jour ---
res_matchs = requests.get(
    f"{SUPABASE_URL}/rest/v1/match?date_match=eq.{date_du_jour}",
    headers=HEADERS_SUPA
)
matchs = res_matchs.json() if res_matchs.status_code == 200 else []

if not matchs:
    print("❌ Pas de matchs planifiés aujourd'hui dans ta BDD.")
else:
    print(f"📅 {len(matchs)} match(s) trouvé(s) pour aujourd'hui.\n")

    # --- ÉTAPE 3 : Aller chercher les compos sur CompoProbable.net ---
    url_site = "https://www.compopropable.net/"
    try:
        response = requests.get(url_site, headers=headers_web)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # On récupère tous les blocs de matchs sur la page d'accueil
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'match|post|entry|card', re.IGNORECASE))
            
            # Si le site est structuré simplement avec des liens
            if not articles:
                articles = soup.find_all('a', href=re.compile(r'/compo|/composition|/match'))

            # Pour chaque match de TA base de données
            for match in matchs:
                dom = equipes_bdd.get(match['id_equipe_dom'], f"ID_{match['id_equipe_dom']}")
                ext = equipes_bdd.get(match['id_equipe_ext'], f"ID_{match['id_equipe_ext']}")
                
                print(f"⚔️ {match.get('nom_champi', 'Match')} : {dom} vs {ext}")
                match_trouve = False

                # On cherche si ce match est présent sur le site
                for article in articles:
                    texte_article = article.text.lower()
                    
                    # On compare les noms de tes équipes avec le texte du lien/article
                    if (dom.lower() in texte_article or ext.lower() in texte_article):
                        # On récupère le lien de la page du match
                        lien = article if article.name == 'a' else article.find('a')
                        if not lien or not lien.get('href'):
                            continue
                            
                        url_match = lien['href']
                        if not url_match.startswith('http'):
                            url_match = "https://www.compopropable.net" + url_match
                        
                        # On va sur la page du match pour extraire les joueurs
                        res_page = requests.get(url_match, headers=headers_web)
                        if res_page.status_code == 200:
                            soup_match = BeautifulSoup(res_page.text, 'html.parser')
                            listes = soup_match.find_all('ul')
                            
                            equipe_index = 0
                            for liste in listes:
                                joueurs = liste.find_all('li')
                                # Une compo contient environ 11 à 18 joueurs (titulaires + remplaçants)
                                if 10 <= len(joueurs) <= 18:
                                    equipe_index += 1
                                    nom_eq = dom if equipe_index == 1 else ext
                                    print(f"   📋 Compo Probable [{nom_eq}] :")
                                    for j in joueurs[:11]: # On affiche le 11 majeur
                                        print(f"      ◽ {j.text.strip()}")
                            match_trouve = True
                        break # Match trouvé, on passe au match suivant de ta BDD
                
                if not match_trouve:
                    print("   ⚠️ Aucune composition disponible pour ce match sur le site actuellement.")
                print("-" * 50)

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion au site de compositions : {e}")

print("\n--- FIN DU SCRIPT ---")