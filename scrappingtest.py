import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

URL_FLASH = "https://www.flashscore.fr/football/angleterre/premier-league/classement/"

def traduire_forme(lettre):
    mapping = {"V": "W", "N": "D", "D": "L"}
    return mapping.get(lettre.upper(), lettre)

def scraper_forme_flashscore():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print(f"📡 Analyse du classement sur : {URL_FLASH}")
    driver.get(URL_FLASH)
    time.sleep(10) # Indispensable pour charger les carrés de forme

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    lignes = soup.find_all('div', class_='ui-table__row')

    for ligne in lignes:
        try:
            nom_equipe = ligne.find('a', class_='tableCellParticipant__name').text.strip()
            
            bloc_forme = ligne.find('div', class_='table__cell--form')
            carres = bloc_forme.select('.tableCellFormIcon')

            print(f"🔄 Traitement de : {nom_equipe}")

            # Utilisation de enumerate pour différencier les 5 matchs
            for index, c in enumerate(carres):
                lettre_brute = c.get_text(strip=True)[:1].upper()
                resultat_en = traduire_forme(lettre_brute)

                # Création d'un ID unique pour éviter l'erreur 400 (Doublon de clé)
                # On combine le timestamp actuel et l'index du match
                unique_id = int(f"{int(time.time())}{index}") 

                payload = {
                    "team_name": str(nom_equipe),
                    "resultat": str(resultat_en),
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "buts_marques": 0, 
                    "buts_encaisses": 0,
                    "match_id": unique_id  # L'ID change maintenant à chaque itération
                }

                res = requests.post(f"{SUPABASE_URL}/rest/v1/forme_equipes", headers=HEADERS_SUPA, json=payload)
                
                if res.status_code == 201:
                    print(f"   ✅ Match {index+1}/5 Ajouté : {resultat_en}")
                else:
                    # Affiche le message d'erreur précis de Supabase si ça échoue encore
                    print(f"   ❌ Erreur insertion : {res.status_code} - {res.text}")

        except Exception as e:
            print(f"⚠️ Erreur sur une ligne : {e}")
            continue

if __name__ == "__main__":
    scraper_forme_flashscore()