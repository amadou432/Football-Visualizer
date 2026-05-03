import requests   #On importe la bibliothèque requests pour pouvoir faire des requêtes HTTP.

from bs4 import BeautifulSoup  #On importe BeautifulSoup depuis la bibliothèque bs4  pour analyser le HTML.

# On choisit le site qu'on veut scraper
url = "https://www.betexplorer.com/football/france/ligue-1/"

#on récupere le site 
#e "User-Agent" c'est très important — sans ça le site croit que c'est un robot
# et refuse de répondre. En mettant un User-Agent on se fait passer pour
# un vrai navigateur Chrome
response = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


# On analyse le HTML de la page
soup = BeautifulSoup(response.text, 'html.parser')
tableaux = soup.find_all("table")

# On affiche juste le titre de la page dont on a mis l'url ( on le recupere direct depuis le code source de la page )
print( soup.title.text)
if tableaux:
    print(tableaux[0])