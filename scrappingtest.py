import requests   #On importe la bibliothèque requests pour pouvoir faire des requêtes HTTP.

from bs4 import BeautifulSoup  #On importe BeautifulSoup depuis la bibliothèque bs4  pour analyser le HTML.

# On choisit le site qu'on veut scraper
url = "https://meilleurssitesdeparissportifs.fr/football_FRA_D_FRE_generic.html#article-0"

#on récupere le site 
response = requests.get(url)

# On analyse le HTML de la page
soup = BeautifulSoup(response.text, 'html.parser')

# On affiche juste le titre de la page dont on a mis l'url ( on le recupere direct depuis le code source de la page )
print("Page récupérée :", soup.title.text)