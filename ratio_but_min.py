
from datetime import datetime
from base import (
    CHAMPIONNATS_SOFA,
    creer_driver, fetch_json, get_tous_les_matchs, get_incidents_match,
    charger_equipes, resoudre_equipe, upsert_supabase
)
import time
import random
 
def get_minutes_joueur(driver, player_id, tournament_id, season_id):
    """Minutes jouées dans la saison pour un joueur via SofaScore."""
    url = (
        f"https://api.sofascore.com/api/v1/player/{player_id}"
        f"/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
    )
    data = fetch_json(driver, url)
    return data.get("statistics", {}).get("minutesPlayed", 0) or 0
 
def get_photo_joueur(player_id):
    """URL de la photo du joueur via SofaScore CDN."""
    return f"https://img.sofascore.com/api/v1/player/{player_id}/image"
 
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print(f"=== SCRAPING RATIO BUT/MIN PAR JOUEUR ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
 
print("Chargement des équipes depuis Supabase...")
equipes_bdd = charger_equipes()
print(f"{len(equipes_bdd)} équipes chargées\n")
 
print("Lancement du navigateur Chrome...")
driver = creer_driver()
driver.get("https://www.sofascore.com/fr/")
time.sleep(random.uniform(3, 5))
print("Cookies récupérés ✅\n")
 
# { id_equipe: { player_id: { nom, buts, tournament_id, season_id } } }
stats_joueurs = {}
equipes_non_trouvees = set()
 
for nom_champi, infos in CHAMPIONNATS_SOFA.items():
    print(f"--- {nom_champi} ---")
    matchs = get_tous_les_matchs(driver, infos["tournament_id"], infos["season_id"])
    print(f"→ {len(matchs)} matchs au total pour {nom_champi}\n")
 
    buts_championnat = 0
 
    for match in matchs:
        match_id = match.get("id")
        home     = match.get("homeTeam", {}).get("name", "")
        away     = match.get("awayTeam", {}).get("name", "")
 
        incidents = get_incidents_match(driver, match_id)
 
        for incident in incidents:
            if incident.get("incidentType") != "goal":
                continue
            if incident.get("incidentClass") == "ownGoal":
                continue
 
            player      = incident.get("player", {})
            player_id   = player.get("id")
            player_name = player.get("name", "Inconnu")
 
            if not player_id:
                continue
 
            is_home    = incident.get("isHome")
            nom_equipe = home if is_home else away
            id_equipe  = resoudre_equipe(nom_equipe, equipes_bdd)
 
            if not id_equipe:
                equipes_non_trouvees.add(nom_equipe)
                continue
 
            if id_equipe not in stats_joueurs:
                stats_joueurs[id_equipe] = {}
 
            if player_id not in stats_joueurs[id_equipe]:
                stats_joueurs[id_equipe][player_id] = {
                    "nom":           player_name,
                    "buts":          0,
                    "tournament_id": infos["tournament_id"],
                    "season_id":     infos["season_id"],
                    "photo":         get_photo_joueur(player_id),  # ✅ photo ajoutée ici
                }
 
            stats_joueurs[id_equipe][player_id]["buts"] += 1
            buts_championnat += 1
 
    print(f"✅ {nom_champi} traité")
    print(f"   📊 {len(matchs)} matchs analysés — saison_id: {infos['season_id']}")
    print(f"   ⚽ {buts_championnat} buts attribués\n")
 
if equipes_non_trouvees:
    print(f"⚠️  Équipes non mappées ({len(equipes_non_trouvees)}) — à ajouter dans MAPPING_EQUIPES (base.py) :")
    for nom in sorted(equipes_non_trouvees):
        print(f"   - {nom}")
    print()
 
# ============================================================
# RÉCUPÉRATION DES MINUTES + CALCUL RATIO
# ============================================================
print("Récupération des minutes jouées par joueur...\n")
 
resultats_finaux = {}
 
for id_equipe, joueurs in stats_joueurs.items():
    joueurs_avec_ratio = []
 
    for player_id, data in joueurs.items():
        minutes = get_minutes_joueur(
            driver, player_id, data["tournament_id"], data["season_id"]
        )
        ratio = round(data["buts"] / minutes, 4) if minutes > 0 else 0.0
 
        joueurs_avec_ratio.append({
            "nom":     data["nom"],
            "buts":    data["buts"],
            "minutes": minutes,
            "ratio":   ratio,
            "photo":   data["photo"],  # ✅
        })
 
    # Tri par ratio décroissant, buts en départage
    joueurs_avec_ratio.sort(key=lambda x: (x["ratio"], x["buts"]), reverse=True)
    resultats_finaux[id_equipe] = joueurs_avec_ratio[:3]
 
driver.quit()
print("Navigateur fermé ✅\n")
 
# ============================================================
# ENREGISTREMENT DANS SUPABASE
# ============================================================
print("--- ENREGISTREMENT DANS SUPABASE ---")
 
for id_equipe, top3 in resultats_finaux.items():
    payload = {}
 
    for i, joueur in enumerate(top3, start=1):
        payload[f"joueur_{i}_nom"]     = joueur["nom"]
        payload[f"joueur_{i}_buts"]    = joueur["buts"]
        payload[f"joueur_{i}_minutes"] = joueur["minutes"]
        payload[f"joueur_{i}_ratio"]   = joueur["ratio"]
        payload[f"joueur_{i}_photo"]   = joueur["photo"]  # ✅
 
    # Slots vides si moins de 3 buteurs
    for i in range(len(top3) + 1, 4):
        payload[f"joueur_{i}_nom"]     = None
        payload[f"joueur_{i}_buts"]    = 0
        payload[f"joueur_{i}_minutes"] = 0
        payload[f"joueur_{i}_ratio"]   = 0.0
        payload[f"joueur_{i}_photo"]   = None  # ✅
 
    upsert_supabase("ratio_but_min", "id_equipe", id_equipe, payload)
    top_noms = " | ".join([j["nom"] for j in top3])
    print(f"✅ Équipe {id_equipe} → {top_noms}")
 
print(f"\n✅ {len(resultats_finaux)} équipes enregistrées dans ratio_but_min")
print("=== FIN ===")
 