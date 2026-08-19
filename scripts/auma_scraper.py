from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    print("Buttons auf der Seite:\n")

    buttons = page.locator("button")

    count = buttons.count()

    for i in range(count):
        try:
            button = buttons.nth(i)

            print(
                f"{i}: "
                f"{button.inner_text()}"
            )
        except:
            pass

    browser.close()
