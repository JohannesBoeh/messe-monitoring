from cities import CITIES

print("Starte AUMA-Scraper...\n")

all_messen = []

for item in CITIES:
    messe = {
        "stadt": item["city"],
        "standortklasse": item["class"]
    }

    all_messen.append(messe)

print(all_messen)
