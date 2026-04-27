"""
fetch_matchs.py
---------------
Lance ce script UNE FOIS PAR JOUR pour remplir Supabase avec les matchs à venir.
Il consomme seulement 1 appel API Football.

Comment lancer :
    python fetch_matchs.py
"""

import requests
from datetime import datetime, timedelta

# ============================================================
# CONFIG — mets tes vraies clés ici
# ============================================================
API_FOOTBALL_KEY = "b49cd48ad7f439af314355b5991ff713"
SUPABASE_URL     = "https://deqthaukwlduxbsbmqgz.supabase.co"      # <-- remplace par ton URL Supabase
SUPABASE_KEY     = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"                           # <-- remplace par ta clé anon Supabase
# ============================================================

# Récupère les matchs de demain (tu peux changer "tomorrow" par "today")
demain = datetime.now().strftime('%Y-%m-%d')

print(f"📅 Récupération des matchs du {demain}...")

# 1. Appel API Football
r = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers={
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_FOOTBALL_KEY
    },
    params={'date': demain}
)
data = r.json()
matchs_raw = data.get('response', [])
print(f"✅ {len(matchs_raw)} matchs trouvés depuis l'API Football")

# 2. Formate les données pour Supabase
matchs_formates = []
for m in matchs_raw:
    matchs_formates.append({
        "id":          m['fixture']['id'],
        "date":        m['fixture']['date'][:10],
        "heure":       m['fixture']['date'][11:16],
        "league_name": m['league']['name'],
        "league_id":   m['league']['id'],
        "season":      m['league']['season'],
        "home_name":   m['teams']['home']['name'],
        "home_logo":   m['teams']['home']['logo'],
        "home_id":     m['teams']['home']['id'],
        "away_name":   m['teams']['away']['name'],
        "away_logo":   m['teams']['away']['logo'],
        "away_id":     m['teams']['away']['id'],
        "venue_name":  m['fixture']['venue']['name'] or "Inconnu",
        "venue_city":  m['fixture']['venue']['city'] or "Inconnu",
        "status":      m['fixture']['status']['short']
    })

# 3. Envoie dans Supabase (upsert = insert ou update si déjà existant)
headers_supa = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"  # upsert
}

resp = requests.post(
    f"{SUPABASE_URL}/rest/v1/matchs",
    headers=headers_supa,
    json=matchs_formates
)

if resp.status_code in [200, 201]:
    print(f"🎉 {len(matchs_formates)} matchs envoyés dans Supabase avec succès !")
else:
    print(f"❌ Erreur Supabase : {resp.status_code} — {resp.text}")