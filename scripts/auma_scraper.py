import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

print("JavaScript-Dateien:\n")

for script in soup.find_all("script", src=True):
    print(script["src"])
