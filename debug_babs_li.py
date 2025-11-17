"""
Debug the actual content of LI elements in BABS
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.thuisbezorgd.nl/en/menu/babs-burritos"
driver.get(url)
time.sleep(5)

print("\n🔍 Checking LI elements in BABS\n")

# Find first category
categories = driver.find_elements(By.CSS_SELECTOR, "section[data-qa*='category']")

if categories:
    first_category = categories[0]

    # Try to get category name
    try:
        h2 = first_category.find_element(By.CSS_SELECTOR, "h2")
        print(f"Category: {h2.text}\n")
    except:
        print("Category: [not found]\n")

    # Find all LI items
    li_items = first_category.find_elements(By.CSS_SELECTOR, "li")
    print(f"Found {len(li_items)} <li> elements\n")

    # Check first few LI items
    for i, li in enumerate(li_items[:3], 1):
        print(f"\n{'=' * 60}")
        print(f"LI ITEM {i}")
        print('=' * 60)

        # Print the full HTML
        html = li.get_attribute('outerHTML')
        print(f"\nFull HTML:\n{html[:800]}...\n")

        # Try to find text content
        print(f"Text content: {li.text}\n")

        # Try all possible selectors for name
        print("Searching for NAME:")
        for selector in ["h3", "h4", "strong", "[class*='name']", "span"]:
            try:
                elem = li.find_element(By.CSS_SELECTOR, selector)
                if elem.text.strip():
                    print(f"  ✓ {selector}: {elem.text}")
            except:
                pass

        # Try all possible selectors for price
        print("\nSearching for PRICE:")
        for selector in ["[data-qa*='price']", "[class*='price']", "span"]:
            try:
                elem = li.find_element(By.CSS_SELECTOR, selector)
                if '€' in elem.text or 'from' in elem.text.lower():
                    print(f"  ✓ {selector}: {elem.text}")
            except:
                pass

print("\n\nPress Enter to close browser...")
input()
driver.quit()