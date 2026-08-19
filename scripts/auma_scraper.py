from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    page.click("#location-input")
    page.fill("#location-input", "Mün")

    page.wait_for_timeout(3000)

    # Ersten Vorschlag auswählen (München)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(2000)

    print("Ausgewählter Wert:")
    print(page.input_value("#location-input"))

    body = page.locator("body").inner_text()

    if "7261" in body:
        print("Noch alle Messen")
    else:
        print("Filter scheint aktiv")

    browser.close()
