import requests
from bs4 import BeautifulSoup

url = "https://www.whoscored.com"

response = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

print(response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.title.text)