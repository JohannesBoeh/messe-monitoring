import requests

url = "https://www.auma.de/messen-finden/messe/dusseldorf_psi_229475"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("URL:")
print(url)

print("\nStatus:")
print(response.status_code)

print("\nFinal URL:")
print(response.url)

print("\nErste 5000 Zeichen:\n")

print(response.text[:5000])
