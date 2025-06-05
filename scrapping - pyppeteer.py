import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
from collections import defaultdict

async def scrape_garden_stock():
    browser = await launch(
        executablePath="/usr/bin/chromium-browser",
        headless=True,
        args=["--no-sandbox"]
    )
    page = await browser.newPage()

    await page.goto("https://www.vulcanvalues.com/grow-a-garden/stock", timeout=60000, waitUntil='domcontentloaded')

    content = await page.content()
    await browser.close()

    soup = BeautifulSoup(content, 'html.parser')
    categorized = defaultdict(list)

    for header in soup.find_all("h2", class_="text-xl font-bold mb-2 text-center"):
        category = header.text.strip()
        ul = header.find_next_sibling("ul")
        if not ul:
            continue

        items = ul.find_all("li", class_="bg-gray-900")
        for item in items:
            name = item.find("img")["alt"]
            quantity = item.find("span", class_="text-gray-400").text.strip()
            categorized[category].append((name, quantity))

    return categorized
