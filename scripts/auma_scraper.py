import requests

print("Teste Verbindung zu AUMA...")

url = "https://www.auma.de"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Inhalt erhalten: {len(response.text)} Zeichen")

print(response.text[:500])
