
from datetime import datetime
from collections import defaultdict
from base import (
    CHAMPIONNATS_SOFA,
    creer_driver, get_tous_les_matchs, get_incidents_match,
    charger_equipes, resoudre_equipe, upsert_supabase
)
import time
import random
 
# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print(f"=== SCRAPING TYPES DE BUTS ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
 
print("Chargement des équipes depuis Supabase...")
equipes_bdd = charger_equipes()
print(f"{len(equipes_bdd)} équipes chargées\n")
 
print("Lancement du navigateur Chrome...")
driver = creer_driver()
driver.get("https://www.sofascore.com/fr/")
time.sleep(random.uniform(3, 5))
print("Cookies récupérés ✅\n")
 
stats_equipes = defaultdict(lambda: {
    "total": 0,
    "normal": 0,
    "penalty": 0,
    "csc": 0,
    "tete": 0,
    "gauche": 0,
    "droite": 0
})
 
equipes_non_trouvees = set()
 
for nom_champi, infos in CHAMPIONNATS_SOFA.items():
    print(f"--- {nom_champi} ---")
 
    # Récupère TOUS les matchs via base.py (pagination complète)
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
 
            # Gestion own goal : attribué à l'équipe adverse
            if incident.get("incidentClass") == "ownGoal":
                equipe_qui_marque = not incident.get("isHome")
            else:
                equipe_qui_marque = incident.get("isHome")
 
            nom_equipe = home if equipe_qui_marque else away
            id_equipe  = resoudre_equipe(nom_equipe, equipes_bdd)
 
            if not id_equipe:
                equipes_non_trouvees.add(nom_equipe)
                continue
 
            s = stats_equipes[id_equipe]
            s["total"] += 1
            buts_championnat += 1
 
            goal_type = (incident.get("goalType") or "").lower()
            shot_type = (incident.get("shotType") or "").lower()
 
            if incident.get("incidentClass") == "ownGoal" or goal_type == "own":
                s["csc"] += 1
            elif goal_type == "penalty":
                s["penalty"] += 1
            else:
                s["normal"] += 1
 
            if shot_type == "header":
                s["tete"] += 1
            elif shot_type == "left-foot":
                s["gauche"] += 1
            elif shot_type == "right-foot":
                s["droite"] += 1
 
    print(f"✅ {nom_champi} traité")
    print(f"   📊 {len(matchs)} matchs analysés — saison_id: {infos['season_id']}")
    print(f"   ⚽ {buts_championnat} buts trouvés\n")
 
if equipes_non_trouvees:
    print(f"⚠️  Équipes non mappées ({len(equipes_non_trouvees)}) :")
    for nom in sorted(equipes_non_trouvees):
        print(f"   - {nom}")
    print()
 
driver.quit()
print("Navigateur fermé ✅\n")
 
# ============================================================
# ENREGISTREMENT DANS SUPABASE
# ============================================================
print("--- ENREGISTREMENT DANS SUPABASE ---")
 
for id_equipe, s in stats_equipes.items():
    if s["total"] == 0:
        continue
 
    total = s["total"]
    payload = {
        "total_buts":       total,
        "buts_normaux":     s["normal"],
        "buts_penalty":     s["penalty"],
        "buts_csc":         s["csc"],
        "buts_tete":        s["tete"],
        "buts_pied_gauche": s["gauche"],
        "buts_pied_droit":  s["droite"],
        "pct_normaux": round(s["normal"]  / total * 100, 2),
        "pct_penalty": round(s["penalty"] / total * 100, 2),
        "pct_csc":     round(s["csc"]     / total * 100, 2),
        "pct_tete":    round(s["tete"]    / total * 100, 2),
        "pct_gauche":  round(s["gauche"]  / total * 100, 2),
        "pct_droite":  round(s["droite"]  / total * 100, 2),
    }
 
    upsert_supabase("type_but_equipes", "id_equipe", id_equipe, payload)
    print(f"✅ Équipe {id_equipe} — {total} buts enregistrés")
 
print(f"\n✅ {len(stats_equipes)} équipes enregistrées dans type_but_equipes")
print("=== FIN ===")