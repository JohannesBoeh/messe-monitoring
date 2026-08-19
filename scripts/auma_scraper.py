from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    # München eintragen
    page.fill("#location-input", "München")

    # Suchbutton klicken
    page.get_by_text("Ergebnisse anzeigen").click()

    page.wait_for_timeout(5000)

    print("URL nach Suche:")
    print(page.url)

    print("\nTitel:")
    print(page.title())

    browser.close()
