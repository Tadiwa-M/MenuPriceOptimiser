"""
Debug why BABS Burritos isn't working
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

print("\n🔍 Debugging BABS Burritos\n")

# Find categories
categories = driver.find_elements(By.CSS_SELECTOR, "section[data-qa*='category']")
print(f"✓ Found {len(categories)} categories\n")

for i, category in enumerate(categories[:3], 1):  # Check first 3 categories
    print(f"\n{'=' * 60}")
    print(f"CATEGORY {i}")
    print('=' * 60)

    # Get category name
    try:
        heading = category.find_element(By.CSS_SELECTOR, "h2")
        print(f"Category name: {heading.text}")
    except:
        print("Category name: [not found]")

    # Count h3 elements
    h3_elements = category.find_elements(By.CSS_SELECTOR, "h3")
    print(f"H3 elements found: {len(h3_elements)}")

    # Print all h3 text
    for j, h3 in enumerate(h3_elements, 1):
        print(f"  {j}. {h3.text}")

    # Look for price elements in this category
    price_elements = category.find_elements(By.CSS_SELECTOR, "[data-qa*='price']")
    print(f"\nPrice elements found: {len(price_elements)}")
    for j, price in enumerate(price_elements[:5], 1):
        print(f"  {j}. {price.text}")

    # Try to find the actual item containers
    print("\nLooking for item containers...")
    possible_containers = [
        "article",
        "[data-qa*='item']",
        "li",
        "div[class*='item']"
    ]

    for selector in possible_containers:
        items = category.find_elements(By.CSS_SELECTOR, selector)
        if items:
            print(f"  ✓ Found {len(items)} elements with: {selector}")
            # Show first item's HTML
            if items:
                html_preview = items[0].get_attribute('outerHTML')[:300]
                print(f"    Preview: {html_preview}...")

print("\n\n" + "=" * 60)
print("Keep browser open? (Press Enter to close)")
input()

driver.quit()