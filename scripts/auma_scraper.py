import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

print("Links auf der Startseite:\n")

for link in soup.find_all("a", href=True):
    text = link.get_text(strip=True)

    if text:
        print(text)
