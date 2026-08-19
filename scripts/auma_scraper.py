from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    print("Seitentitel:")
    print(page.title())

    print("\nAlle Input-Felder:")

    inputs = page.locator("input")

    count = inputs.count()

    for i in range(count):
        try:
            field = inputs.nth(i)

            print(
                f"{i}: "
                f"id={field.get_attribute('id')} "
                f"name={field.get_attribute('name')} "
                f"placeholder={field.get_attribute('placeholder')}"
            )
        except:
            pass

    browser.close()
