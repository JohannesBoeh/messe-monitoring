from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.auma.de/messen-finden/",
        wait_until="networkidle"
    )

    links = page.locator("a")

    print("Suche PSI-Links...\n")

    count = links.count()

    for i in range(count):

        try:

            href = links.nth(i).get_attribute("href")
            text = links.nth(i).inner_text().strip()

            if "PSI" in text:

                print("TEXT:")
                print(text)

                print("\nHREF:")
                print(href)

                print("\n" + "=" * 80)

        except:
            pass

    browser.close()
