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

```
equipe          — Informations sur les équipes (nom, logo)
match           — Matchs à venir (date, heure, championnat, équipes)
cote            — Cotes 1/N/2 par bookmaker
joueur          — Informations sur les joueurs
forme_equipe    — Informations sur les matchs précèdents des equipes(buts marqués, buts encaissés,...)
```

## 🔄 Récupération des données

### Via API Football

Les données des matchs et des cotes sont récupérées automatiquement via **API Football** (plan gratuit — 100 requêtes/jour).

**Ce qu'on récupère :**

- Liste des matchs du jour pour les 5 grands championnats
- Meilleures cotes 1/N/2 avec le nom du bookmaker
- Logos et informations des équipes

**Fonctionnement :**
API Football → Script Python → Supabase (stockage) → Site web (affichage)
Les données sont récupérées de deux façons différentes :

### Via API Football

Certaines données sont récupérées automatiquement via **API Football** (plan gratuit — 100 requêtes/jour) :

- La liste des matchs du jour pour les 5 grands championnats
- Les meilleures cotes 1/N/2 avec le nom du bookmaker associé

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
