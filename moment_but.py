
from datetime import datetime
from base import (
    CHAMPIONNATS_SOFA,
    creer_driver, get_tous_les_matchs, get_incidents_match,
    charger_equipes, resoudre_equipe, upsert_supabase
)
import time
import random

def determiner_tranche(minute):
    """Détermine la tranche horaire correspondante à la minute du but."""
    if minute is None:
        return None
    if 0 <= minute <= 15:
        return "tranche_0_15"
    elif 16 <= minute <= 30:
        return "tranche_16_30"
    elif 31 <= minute <= 45:
        return "tranche_31_45"
    elif 46 <= minute <= 60:
        return "tranche_46_60"
    elif 61 <= minute <= 75:
        return "tranche_61_75"
    else:
        return "tranche_76_90"

# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================
print(f"=== SCRAPING MOMENTS DE BUTS ({datetime.now().strftime('%Y-%m-%d')}) ===\n")

print("Chargement des équipes depuis Supabase...")
equipes_bdd = charger_equipes()
print(f"{len(equipes_bdd)} équipes chargées\n")

print("Lancement du navigateur Chrome...")
driver = creer_driver()
driver.get("https://www.sofascore.com/fr/")
time.sleep(random.uniform(3, 5))
print("Cookies récupérés ✅\n")

stats_equipes = {}
equipes_non_trouvees = set()

for nom_champi, infos in CHAMPIONNATS_SOFA.items():
    print(f"--- {nom_champi} ---")

    # Récupère TOUS les matchs de la saison via la fonction globale de base.py
    matchs = get_tous_les_matchs(driver, infos["tournament_id"], infos["season_id"])
    print(f"→ {len(matchs)} matchs au total pour {nom_champi}\n")

    buts_championnats = 0

    for match in matchs:
        match_id = match.get("id")
        home = match.get("homeTeam", {}).get("name", "")
        away = match.get("awayTeam", {}).get("name", "")

        
        incidents = get_incidents_match(driver, match_id)

        for incident in incidents:
            if incident.get("incidentType") != "goal":
                continue

            minute = incident.get("time")

            # GESTION OWN GOAL :
            # Si c'est un but contre son camp, on l'attribue à l'équipe ADVERSE
            if incident.get("incidentClass") == "ownGoal":
                equipe_qui_marque = not incident.get("isHome")  # Inverser !
            else:
                equipe_qui_marque = incident.get("isHome")

            nom_equipe = home if equipe_qui_marque else away
            
            # Utilisation du mapping ultra-sécurisé de base.py
            id_equipe = resoudre_equipe(nom_equipe, equipes_bdd)

            if not id_equipe:
                equipes_non_trouvees.add(nom_equipe)
                continue

            tranche = determiner_tranche(minute)
            if not tranche:
                continue

            if id_equipe not in stats_equipes:
                stats_equipes[id_equipe] = {
                    "tranche_0_15": 0, "tranche_16_30": 0,
                    "tranche_31_45": 0, "tranche_46_60": 0,
                    "tranche_61_75": 0, "tranche_76_90": 0,
                    "total_buts": 0
                }

            stats_equipes[id_equipe][tranche] += 1
            stats_equipes[id_equipe]["total_buts"] += 1
            buts_championnats += 1

    print(f"✅ {nom_champi} traité")
    print(f"   📊 {len(matchs)} matchs analysés — saison_id: {infos['season_id']}")
    print(f"   ⚽ {buts_championnats} buts trouvés sur ce championnat\n")

driver.quit()
print("Navigateur fermé ✅\n")

if equipes_non_trouvees:
    print(f"⚠️  Équipes non mappées ({len(equipes_non_trouvees)}) — à vérifier dans base.py :")
    for nom in sorted(equipes_non_trouvees):
        print(f"   - {nom}")
    print()

# ============================================================
# ENREGISTREMENT DANS SUPABASE
# ============================================================
print("--- ENREGISTREMENT DANS SUPABASE ---")
for id_equipe, stats in stats_equipes.items():
    # Utilisation de la fonction upsert générique avec retry automatique
    upsert_supabase("moment_but", "id_equipe", id_equipe, stats)
    print(f"✅ Équipe {id_equipe} — {stats['total_buts']} buts enregistrés")

print(f"\n✅ {len(stats_equipes)} équipes enregistrées dans moment_but")
print("=== FIN ===")