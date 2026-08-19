import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

print("Links mit URL:\n")

for link in soup.find_all("a", href=True):
    text = link.get_text(strip=True)

    if "Messen finden" in text:
        print("TEXT:", text)
        print("URL :", link["href"])
        print("-" * 50)
