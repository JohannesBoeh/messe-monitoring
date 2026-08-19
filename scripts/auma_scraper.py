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

    print("Autocomplete Inhalte:")

    body = page.locator("body").inner_text()

    for line in body.splitlines():
        if "Mün" in line:
            print(line)

    browser.close()
