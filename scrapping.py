from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from collections import defaultdict
import asyncio


async def scrape_garden_stock():
    # launching chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-cache")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disk-cache-size=0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # access and load the page
    driver.get("https://www.vulcanvalues.com/grow-a-garden/stock")
    #time.sleep(3)
    await asyncio.sleep(3)

    # Gather html code then clsoe
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # dict to store and sort into category
    categorized = defaultdict(list)
    #print("!!!! new dict updated !!!!")

    # Get each category header and its next sibling <ul>
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

    # DEBUG: print categorized result
    # for category, items in categorized.items():
    #     print(f"\n== {category} ==")
    #     for name, qty in items:
    #         print(f"{name}: {qty}")

    return categorized


#scrape_garden_stock()