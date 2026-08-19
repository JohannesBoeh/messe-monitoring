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

    print("Autocomplete-Einträge:")

    options = page.locator("li")

    count = min(options.count(), 50)

    for i in range(count):
        try:
            text = options.nth(i).inner_text().strip()

            if text:
                print(i, text)
        except:
            pass

    browser.close()
