import requests

print("Lade AUMA Startseite...")

url = "https://www.auma.de"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

with open("output/auma_homepage.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Datei gespeichert.")
