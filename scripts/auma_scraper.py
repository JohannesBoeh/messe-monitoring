from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.fill("#location-input", "München")

    page.wait_for_timeout(3000)

    print("Wert:")
    print(page.input_value("#location-input"))

    print("\nAnzahl Ergebnisse anzeigen:")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        try:
            text = buttons.nth(i).inner_text().strip()

            if "Ergebnisse" in text:
                print(i, text)

        except:
            pass

    browser.close()
