from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()
    page = context.new_page()

    page.goto("http://10.42.0.246:3000")

    input(
        "Log into Grafana manually and open the dashboard, then press Enter..."
    )

    context.storage_state(path="state.json")

    print("Session saved to state.json")

    browser.close()
