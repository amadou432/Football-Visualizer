# ⚽ Football Visualizer

Football Visualizer est un site web de visualisation de statistiques sur les matchs de football, conçu pour guider les utilisateurs dans leurs choix de paris sportifs.

---

## 📋 Description

Football Visualizer affiche les matchs à venir des 5 grands championnats européens avec leurs cotes, statistiques et un indice de confiance calculé automatiquement.

### Championnats couverts

- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
- 🇫🇷 Ligue 1
- 🇪🇸 La Liga
- 🇮🇹 Serie A
- 🇩🇪 Bundesliga

---

## 🛠️ Stack technique

### Backend

- **Python 3.11** — langage principal
- **Flask** — framework web Python pour gérer les routes et les templates
- **Supabase (Python SDK)** — client Python pour interagir avec la base de données
- **python-dotenv** — gestion des variables d'environnement (.env)

### Frontend

- **HTML5 / CSS3** — structure et design du site
- **Jinja2** — moteur de templates Flask pour afficher les données dynamiquement
- **Chart.js** — bibliothèque JavaScript pour les graphiques (radar de performance)
- **Google Fonts** — polices Bebas Neue et DM Sans

### Base de données

- **Supabase** — base de données PostgreSQL hébergée en ligne
- **Looping** — outil de modélisation de la base de données (MCD/MLD)

### Scraping

- **requests** — récupération du contenu HTML des pages web
- **BeautifulSoup4** — extraction des données depuis le HTML
- **API Football** — API pour récupérer les matchs et statistiques (100 appels/jour)

### Hébergement

- **Vercel** — hébergement du site web (frontend)
- **Railway** — exécution du scraper Python en arrière-plan

---

## 🗄️ Structure de la base de données

L'application s'appuie sur une base de données PostgreSQL hébergée sur Supabase, structurée de la manière suivante :

* **`match`** : Table centrale contenant le calendrier des matchs à venir (identifiant, date, heure du coup d'envoi, nom du championnat, ainsi que les clés étrangères associant l'équipe à domicile et l'équipe à l'extérieur).
* **`equipe`** : Référentiel des clubs regroupant les informations signalétiques des équipes (nom officiel, URL du logo/blason).
* **`cote`** : Table de comparaison des cotes de paris sportifs (1/N/2) mise à jour en temps réel avec identification des meilleures cotes et des bookmakers associés (Winamax, Betclic, Unibet, PMU...).
* **`joueur`** : Base de données des joueurs utilisée pour générer et afficher les **compositions probables** des équipes avant le coup d'envoi.
* **`forme_equipes`** : Table analytique mémorisant l'historique et l'état de forme récent des clubs (séries de matchs, buts marqués, buts encaissés).
* **`moment_but`** : Table de distribution temporelle permettant d'analyser à quels moments d'un match (intervalles de minutes) les équipes ont tendance à marquer ou concéder des buts.
* **`absent`** : Registre de suivi des indisponibilités (joueurs blessés, suspendus ou incertains pour les prochaines rencontres).

## 🔄 Récupération des données

# 🔄 Récupération des données

Les données de l'application sont centralisées automatiquement en combinant deux API distinctes afin de respecter les quotas des plans gratuits :

### 📅 Calendrier & Matchs (Via Football-Data.org)
Les informations concernant le calendrier et les équipes sont récupérées via l'API **Football-Data.org** :
* La liste des matchs à venir pour les 5 grands championnats européens (couvrant une fenêtre de J à J+9).
* Les informations signalétiques des clubs (noms officiels et URLs des logos/blasons).

### 📊 Cotes & Bookmakers (Via The Odds API)
Les données de paris sportifs sont récupérées via **The Odds API** (plan gratuit) :
* Les cotes 1/N/2 du marché français mis à jour en temps réel.
* Le filtrage et l'extraction de la meilleure cote disponible associée au nom de son bookmaker (Winamax, Betclic, Unibet, PMU...).

**Flux de fonctionnement :**
Football-Data.org + The Odds API ➔ Scripts Python (Filtrage & Mapping) ➔ Supabase (Stockage) ➔ Site Web (Affichage)
### Via Web Scrapping

D'autres données sont récupérées par **web scrapping** sur des sites de référence comme **Transfermarkt** et **Flashscore** :

- Les joueurs absents (blessés/suspendus) pour chaque match
- Les compositions probables des équipes

---

## 📁 Structure du projet

```
Football-Visualizer/
├── app_bdd.pypy                  # Serveur Flask principal
├── .env                    # Clés API (ne pas commiter !)
├── .gitignore              # Fichiers ignorés par Git
├── requirements.txt        # Dépendances Python
├── static/
│   ├── style.css           # Styles CSS
│   └── logo.png            # Logo du site
├── templates/
│   ├── home.html           # Page d'accueil (liste des matchs)
│   └── match.html          # Page détail d'un match
└── scrapers/
    └── scrappingtest.py    # Script de test de scraping
```

---

## 🚀 Installation et lancement

### Prérequis

- Python 3.11
- Un compte Supabase

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/amadou432/Football-Visualizer.git
cd Football-Visualizer

# 2. Installer les dépendances
py -3.11 -m pip install flask supabase python-dotenv

# 3. Créer le fichier .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=ta_clé_anon_ici

# 4. Lancer le serveur
py -3.11 app.py
```

### Accéder au site

Ouvre **<http://127.0.0.1:5001>** dans ton navigateur.

---

## 🌐 Fonctionnalités

- ✅ Affichage des matchs par championnat
- ✅ Filtrage par championnat (Premier League, Ligue 1, La Liga, Serie A, Bundesliga)
- ✅ Affichage des logos et noms des équipes
- ✅ Affichage des cotes 1/N/2
- ✅ Page détail d'un match avec radar de performance
- ✅ Indice de confiance
- 🔄 Scraping automatique des données (en cours)

---

---

## ⚠️ Notes importantes

- Ne jamais commiter le fichier `.env` sur GitHub
- L'API Football est limitée à **100 appels/jour** sur le plan gratuit
- Supabase est limité à **500 MB** de stockage sur le plan gratuit
- Python 3.14 n'est pas compatible avec les bibliothèques utilisées — utiliser **Python 3.11**
