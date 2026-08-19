from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    # München auswählen
    page.click("#location-input")
    page.fill("#location-input", "Mün")

    page.wait_for_timeout(2000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(2000)

    print("Suche nach 'Ergebnisse anzeigen'...")

    buttons = page.locator("button")

    count = buttons.count()

    for i in range(count):
        try:
            text = buttons.nth(i).inner_text().strip()

            if "Ergebnisse anzeigen" in text:
                print("GEFUNDEN:")
                print("Index:", i)
                print("Text :", text)
        except:
            pass

    browser.close()
