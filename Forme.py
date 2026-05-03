
import requests

# ============================================================
# CONFIG
# ============================================================
API_FOOTBALL_KEY = "b49cd48ad7f439af314355b5991ff713"
SUPABASE_URL     = "https://deqthaukwlduxbsbmqgz.supabase.co"
SUPABASE_KEY     = "sb_publishable_QH_SEUy1i6Uc7QBtAQfr7Q_XeTOeDIK"

CHAMPIONNATS = [
    {"league_id": 39,  "name": "Premier League", "season": 2024},
    {"league_id": 61,  "name": "Ligue 1",         "season": 2024},
    {"league_id": 140, "name": "La Liga",          "season": 2024},
    {"league_id": 135, "name": "Serie A",          "season": 2024},
    {"league_id": 78,  "name": "Bundesliga",       "season": 2024},
]

API_HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_FOOTBALL_KEY
}

SUPA_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}


def get_api(endpoint, params):
    """Appelle l'API Football"""
    try:
        r = requests.get(
            f"https://v3.football.api-sports.io/{endpoint}",
            headers=API_HEADERS,
            params=params
        )
        return r.json().get('response', [])
    except:
        return []


def appels_restants():
    """Vérifie combien d'appels API il reste aujourd'hui"""
    try:
        r = requests.get(
            "https://v3.football.api-sports.io/status",
            headers=API_HEADERS
        )
        data = r.json().get('response', {})
        current = data.get('requests', {}).get('current', 0)
        limit   = data.get('requests', {}).get('limit_day', 100)
        return limit - current
    except:
        return 0


def envoyer_supabase(data):
    """Envoie les données dans Supabase"""
    if not data:
        return True
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/forme_equipes",
        headers=SUPA_HEADERS,
        json=data
    )
    return resp.status_code in [200, 201]


# ============================================================
# ÉTAPE 1 — Vérifie les appels restants
# ============================================================
restants = appels_restants()
print(f"⚡ Appels API restants : {restants}/100")

if restants < 10:
    print("❌ Pas assez d'appels restants. Réessaie demain !")
    exit()

# ============================================================
# ÉTAPE 2 — Récupère toutes les équipes des 5 championnats
# ============================================================
print("\n🏆 Récupération des équipes...\n")

toutes_equipes = []

for champ in CHAMPIONNATS:
    print(f"  → {champ['name']}...", end=" ")

    # 1 appel API pour avoir toutes les équipes du championnat
    equipes = get_api('teams', {
        'league':  champ['league_id'],
        'season':  champ['season']
    })

    for e in equipes:
        toutes_equipes.append({
            "team_id":    e['team']['id'],
            "team_name":  e['team']['name'],
            "league":     champ['name']
        })

    print(f"{len(equipes)} équipes")

print(f"\n✅ {len(toutes_equipes)} équipes au total")

# Limite selon les appels restants
# On garde 5 appels de marge pour ne pas tout épuiser
max_equipes = restants - 5
if len(toutes_equipes) > max_equipes:
    print(f"⚠️  On va traiter seulement {max_equipes} équipes aujourd'hui")
    print(f"   Relance demain pour les équipes restantes")
    toutes_equipes = toutes_equipes[:max_equipes]

# ============================================================
# ÉTAPE 3 — Récupère les 5 derniers matchs de chaque équipe
# ============================================================
print(f"\n📊 Récupération de la forme ({len(toutes_equipes)} équipes)...\n")

total_inseres = 0

for i, equipe in enumerate(toutes_equipes):
    team_id   = equipe['team_id']
    team_name = equipe['team_name']

    print(f"  [{i+1}/{len(toutes_equipes)}] {team_name}...", end=" ")

    # 1 appel API — les 5 derniers matchs terminés de cette équipe
    derniers = get_api('fixtures', {
        'team':   team_id,
        'last':   5,
        'status': 'FT'
    })

    if not derniers:
        print("aucun match")
        continue

    # Formate les données
    forme_data = []
    for m in derniers:
        home_id    = m['teams']['home']['id']
        home_name  = m['teams']['home']['name']
        away_name  = m['teams']['away']['name']
        home_goals = m['goals']['home'] or 0
        away_goals = m['goals']['away'] or 0

        # Est-ce que cette équipe jouait à domicile ?
        est_domicile = (team_id == home_id)

        # Buts marqués et encaissés selon domicile/extérieur
        if est_domicile:
            buts_m    = home_goals
            buts_e    = away_goals
            adversaire = away_name
        else:
            buts_m    = away_goals
            buts_e    = home_goals
            adversaire = home_name

        # Résultat W/D/L
        if buts_m > buts_e:    resultat = 'W'
        elif buts_m == buts_e: resultat = 'D'
        else:                   resultat = 'L'

        forme_data.append({
            "team_id":        team_id,
            "team_name":      team_name,
            "match_id":       m['fixture']['id'],
            "date":           m['fixture']['date'][:10],
            "buts_marques":   buts_m,
            "buts_encaisses": buts_e,
            "resultat":       resultat,
            "domicile":       est_domicile,
            "adversaire":     adversaire
        })

    # Envoie dans Supabase
    succes = envoyer_supabase(forme_data)
    total_inseres += len(forme_data)

    # Affiche la forme ex: W W D L W
    forme_str = ' '.join([f['resultat'] for f in forme_data])
    statut    = "✅" if succes else "❌"
    print(f"{statut} {forme_str}")


# ============================================================
# RÉSUMÉ FINAL
# ============================================================
print(f"\n{'='*50}")
print(f"🎉 Terminé !")
print(f"   {len(toutes_equipes)} équipes traitées")
print(f"   {total_inseres} entrées stockées dans Supabase")
print(f"{'='*50}\n")