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

    page.wait_for_timeout(2000)

    buttons = page.locator("button")

    print("BUTTONS:\n")

    count = buttons.count()

    for i in range(count):
        try:
            btn = buttons.nth(i)

            print(
                i,
                "|",
                btn.inner_text().strip(),
                "|",
                btn.get_attribute("aria-controls"),
                "|",
                btn.get_attribute("type")
            )
        except:
            pass

    browser.close()
