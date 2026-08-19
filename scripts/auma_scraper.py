from cities import CITIES
import requests

print("Teste Verbindung zu AUMA...")

url = "https://www.auma.de"

response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Inhalt erhalten: {len(response.text)} Zeichen")
