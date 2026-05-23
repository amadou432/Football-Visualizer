import requests
import time
import random
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
SUPABASE_URL = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY = "sb_secret_xv1e1Yjbv5eJ6rVcWQPbUQ_IQQpN8r2"
 
HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
 
POSTES = {
    "G": "Gardien", "D": "Défenseur", "M": "Milieu", "F": "Attaquant",
    "GK": "Gardien", "goalkeeper": "Gardien", "defender": "Défenseur",
    "midfielder": "Milieu", "forward": "Attaquant",
}
 
# ============================================================
# FONCTIONS
# ============================================================
 
def creer_driver():
    """Crée un navigateur Chrome qui ressemble à un humain — identique à moment_but.py"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver
 
def fetch_json(driver, url):
    """Utilise Selenium pour récupérer du JSON depuis Sofascore — identique à moment_but.py"""
    driver.get(url)
    time.sleep(random.uniform(2, 4))
    try:
        body = driver.find_element("tag name", "body").text
        return json.loads(body)
    except:
        return {}
 
def normaliser_poste(poste_raw):
    if not poste_raw:
        return "Inconnu"
    return POSTES.get(poste_raw, poste_raw)
 
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print(f"=== SCRAPING COMPOS PROBABLES ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
 
# --- ÉTAPE 1 : Récupérer les matchs à venir depuis Supabase ---
# ✅ FIX CLÉ : id_match dans ta BDD = id Sofascore directement
# Pas besoin de mapping par noms d'équipes — on appelle /lineups avec l'id_match directement
print("Chargement des matchs à venir depuis Supabase...")
aujourd_hui = datetime.now().strftime('%Y-%m-%d')
dans_7_jours = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
 
res = requests.get(
    f"{SUPABASE_URL}/rest/v1/match"
    f"?date_match=gte.{aujourd_hui}"
    f"&date_match=lte.{dans_7_jours}"
    f"&select=id_match,date_match,nom_champi,id_equipe_dom,id_equipe_ext",
    headers=HEADERS_SUPA
).json()
 
matchs_a_venir = res if isinstance(res, list) else []
print(f"{len(matchs_a_venir)} matchs trouvés dans les 7 prochains jours")
 
if not matchs_a_venir:
    print("Aucun match à venir, arrêt du script.")
    exit()
 
# --- ÉTAPE 2 : Charger les équipes (pour afficher les noms dans les logs) ---
print("Chargement des équipes...")
equipes_bdd = {}
for offset in [0, 1000]:
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/equipe?select=id_equipe,nom_equipe&offset={offset}&limit=1000",
        headers=HEADERS_SUPA
    ).json()
    for e in res:
        equipes_bdd[e["id_equipe"]] = e["nom_equipe"]
print(f"{len(equipes_bdd)} équipes chargées\n")
 
# --- ÉTAPE 3 : Vider la table compo_probable (repart à zéro comme absent) ---
print("Vidage de la table compo_probable...")
requests.delete(
    f"{SUPABASE_URL}/rest/v1/joueur?id_compo=gte.0",
    headers=HEADERS_SUPA
)
print("Table vidée ✅\n")
 
# --- ÉTAPE 4 : Lancer le navigateur (identique à moment_but.py) ---
print("Lancement du navigateur Chrome...")
driver = creer_driver()
driver.get("https://www.sofascore.com/fr/")
time.sleep(random.uniform(3, 5))
print("Cookies récupérés ✅\n")
 
# --- ÉTAPE 5 : Pour chaque match, appeler /lineups directement avec l'id_match ---
print("--- SCRAPING LINEUPS ---")
total_joueurs = 0
matchs_avec_compo = 0
matchs_sans_compo = []
 
for match in matchs_a_venir:
    id_match      = match["id_match"]       # ← C'est directement l'ID Sofascore !
    id_equipe_dom = match["id_equipe_dom"]
    id_equipe_ext = match["id_equipe_ext"]
    nom_dom = equipes_bdd.get(id_equipe_dom, f"Équipe {id_equipe_dom}")
    nom_ext = equipes_bdd.get(id_equipe_ext, f"Équipe {id_equipe_ext}")
 
    print(f"\n⚽ {nom_dom} vs {nom_ext} ({match['date_match']} — {match['nom_champi']})")
 
    # Appel direct — pas de recherche par nom, pas de mapping
    url_lineups = f"https://api.sofascore.com/api/v1/event/{id_match}/lineups"
    data = fetch_json(driver, url_lineups)
 
    # Debug : affiche ce que retourne Sofascore si problème
    if not data:
        print(f"   ⚠️  Réponse vide (id_match={id_match})")
        matchs_sans_compo.append(f"{nom_dom} vs {nom_ext} — réponse vide")
        continue
 
    if "home" not in data and "away" not in data:
        cles = list(data.keys())
        print(f"   ⚠️  Pas de lineup — clés reçues : {cles}")
        matchs_sans_compo.append(f"{nom_dom} vs {nom_ext} — clés: {cles}")
        continue
 
    matchs_avec_compo += 1
    compo_sides = [
        ("home", id_equipe_dom),
        ("away", id_equipe_ext),
    ]
 
    for side, id_equipe in compo_sides:
        players = data.get(side, {}).get("players", [])
        print(f"   → {side} ({equipes_bdd.get(id_equipe, id_equipe)}) : {len(players)} joueurs")
 
        for player_info in players:
            player    = player_info.get("player", {})
            nom       = player.get("name", "Inconnu")
            numero    = player_info.get("shirtNumber")
            titulaire = not player_info.get("substitute", True)
            poste_raw = player_info.get("position") or player.get("position") or ""
            poste     = normaliser_poste(poste_raw)
 
            id_joueur_sofa = player.get("id")
            photo = f"https://api.sofascore.app/api/v1/player/{id_joueur_sofa}/image" if id_joueur_sofa else None
 
            payload = {
                "id_match":     id_match,
                "id_equipe":    id_equipe,
                "nom_joueur":   nom,
                "poste":        poste,
                "numero":       numero,
                "titulaire":    titulaire,
                "photo_joueur": photo,
            }
 
            post_res = requests.post(
                f"{SUPABASE_URL}/rest/v1/joueur",
                headers=HEADERS_SUPA,
                json=payload
            )
 
            if post_res.status_code == 201:
                total_joueurs += 1
                statut = "titulaire" if titulaire else "remplaçant"
                print(f"      ✅ {nom} ({poste} — {statut})")
            else:
                print(f"      ❌ {nom} : {post_res.status_code} — {post_res.text}")
 
# --- ÉTAPE 6 : Fermer le navigateur ---
driver.quit()
print("\nNavigateur fermé ✅")
 
# --- RÉSUMÉ FINAL ---
print(f"\n{'='*50}")
print(f"✅ {total_joueurs} joueurs enregistrés au total")
print(f"✅ {matchs_avec_compo}/{len(matchs_a_venir)} matchs avec compo disponible")
 
if matchs_sans_compo:
    print(f"\n⚠️  Matchs sans compo ({len(matchs_sans_compo)}) :")
    for m in matchs_sans_compo:
        print(f"   - {m}")
 
print("=== FIN ===")