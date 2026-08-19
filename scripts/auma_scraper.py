import requests

url = "https://www.auma.de/_assets/743126a2ee7e65eef5e1c170709da15d/dist/js/init.min.js"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(response.text[:3000])
