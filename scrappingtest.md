# 🕷️ Scraping Test — Football Visualizer

Ce fichier explique le code de scraping utilisé pour récupérer les matchs de Ligue 1.

## 📦 Les bibliothèques utilisées

### `requests`
Permet de faire des requêtes HTTP en Python, c'est-à-dire **récupérer le contenu d'une page web** comme le ferait un navigateur (Chrome, Firefox...).

Installation :
```bash
py -m pip install requests
```

### `beautifulsoup4`
Permet d'**analyser et extraire des données** depuis le HTML d'une page web. C'est comme utiliser F12 dans ton navigateur mais en Python.

Installation :
```bash
py -m pip install beautifulsoup4
```

---

## 📄 Le code expliqué ligne par ligne

```python
import requests
```
> On importe la bibliothèque `requests` pour pouvoir faire des requêtes HTTP.

---

```python
from bs4 import BeautifulSoup
```
> On importe `BeautifulSoup` depuis la bibliothèque `bs4` (autre nom de beautifulsoup4) pour analyser le HTML.

---

```python
url = "https://fbref.com/fr/comps/13/calendrier/Scores-et-tableaux-Ligue-1"
```
> On stocke l'adresse du site qu'on veut scraper dans une variable `url`.
> Ici c'est la page des matchs de Ligue 1 sur fbref.com.

---

```python
headers = {"User-Agent": "Mozilla/5.0"}
```
> Par défaut, quand Python fait une requête, les sites détectent que c'est un bot et bloquent la requête.
> En ajoutant un `User-Agent`, on fait **semblant d'être un vrai navigateur** pour ne pas être bloqué.

---

```python
response = requests.get(url, headers=headers)
```
> On envoie une requête GET à l'URL avec nos headers.
> C'est comme **ouvrir la page dans ton navigateur**.
> Le résultat (le HTML de la page) est stocké dans la variable `response`.

---

```python
soup = BeautifulSoup(response.text, 'html.parser')
```
> On analyse le HTML de la page avec BeautifulSoup.
> - `response.text` → le contenu HTML brut de la page
> - `'html.parser'` → le moteur utilisé pour analyser le HTML
> Le résultat est stocké dans `soup`, on pourra ensuite chercher des éléments dedans.

---

```python
print("✅ Page récupérée :", soup.title.text)
```
> On affiche le titre de la page pour vérifier que tout fonctionne.
> - `soup.title` → cherche la balise `<title>` dans le HTML
> - `.text` → récupère juste le texte sans les balises HTML

---

## 🧠 Résumé visuel

```
URL du site
    ↓
requests.get() → récupère le HTML
    ↓
BeautifulSoup → analyse le HTML
    ↓
soup.title.text → extrait les données
```

---

## ▶️ Comment lancer le script

```bash
py .\scrappingtest.py
```

Si tout fonctionne tu devrais voir :
```
✅ Page récupérée : Ligue 1 Scores et tableaux - FBref.com
```