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

    page.wait_for_timeout(2000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    print("Buttons mit 'Ergebnisse':")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        try:
            text = buttons.nth(i).inner_text().strip()

            if "Ergebnisse" in text:
                print(f"{i}: {text}")
        except:
            pass

    browser.close()
