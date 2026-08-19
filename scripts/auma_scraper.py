import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

print("\nTitel der Seite:")
print(soup.title.text)
