import requests
from bs4 import BeautifulSoup

url = "https://www.auma.de/messen-finden/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

forms = soup.find_all("form")

print(f"Anzahl Formulare: {len(forms)}")

for i, form in enumerate(forms):
    print(f"\n--- FORMULAR {i+1} ---")
    print(form.get("action"))
    print(form.get("method"))
