"""
Debug Scraper - Find the Right HTML Selectors
This will help us discover the correct CSS selectors for Thuisbezorgd
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time


def inspect_thuisbezorgd_page(url):
    """Open a page and dump the HTML structure to help find selectors"""

    # Setup Chrome
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print(f"\n🔍 Inspecting: {url}\n")

    try:
        # Load page
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load

        # Try to close cookie popup if it exists
        try:
            cookie_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            for button in cookie_buttons[:5]:  # Check first 5 buttons
                text = button.text.lower()
                if any(word in text for word in ['accept', 'agree', 'akkoord', 'toestaan']):
                    print(f"🍪 Clicking cookie button: {button.text}")
                    button.click()
                    time.sleep(2)
                    break
        except:
            print("No cookie popup found or couldn't close it")

        # Save full HTML to file for inspection
        with open('page_html.txt', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✓ Saved full HTML to 'page_html.txt'\n")

        # Try to find menu sections
        print("=" * 60)
        print("SEARCHING FOR MENU STRUCTURE")
        print("=" * 60)

        # Look for common div/section patterns
        selectors_to_try = [
            ("div[data-qa*='menu']", "Menu container (data-qa)"),
            ("section[data-qa*='category']", "Category sections"),
            ("[class*='menu']", "Classes with 'menu'"),
            ("[class*='meal']", "Classes with 'meal'"),
            ("[class*='dish']", "Classes with 'dish'"),
            ("[class*='item']", "Classes with 'item'"),
            ("[class*='product']", "Classes with 'product'"),
            ("article", "Article elements"),
            ("li", "List items"),
        ]

        for selector, description in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n✓ Found {len(elements)} elements: {description}")
                    print(f"   Selector: {selector}")

                    # Print first element's HTML
                    if len(elements) > 0:
                        first_html = elements[0].get_attribute('outerHTML')[:500]
                        print(f"   First element preview:\n   {first_html}...\n")
            except:
                pass

        # Look for price elements
        print("\n" + "=" * 60)
        print("SEARCHING FOR PRICE ELEMENTS")
        print("=" * 60)

        price_selectors = [
            "[class*='price']",
            "[data-qa*='price']",
            "span:contains('€')",
            "[class*='cost']",
        ]

        for selector in price_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n✓ Found {len(elements)} price elements with: {selector}")
                    # Print a few examples
                    for i, elem in enumerate(elements[:3]):
                        print(f"   Example {i + 1}: {elem.text}")
            except:
                pass

        # Look for item names
        print("\n" + "=" * 60)
        print("SEARCHING FOR ITEM NAMES")
        print("=" * 60)

        name_selectors = [
            "h3",
            "h4",
            "[class*='name']",
            "[class*='title']",
            "[data-qa*='name']",
            "strong",
        ]

        for selector in name_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n✓ Found {len(elements)} elements with: {selector}")
                    # Print a few examples
                    for i, elem in enumerate(elements[:5]):
                        text = elem.text.strip()
                        if text and len(text) < 100:  # Filter out long text blocks
                            print(f"   Example {i + 1}: {text}")
            except:
                pass

        print("\n" + "=" * 60)
        print("INSPECTION COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Check 'page_html.txt' to see the full HTML")
        print("2. Look for patterns in the output above")
        print("3. Find the correct selectors for menu items")
        print("\nKeep the browser open to manually inspect? (Press Enter to close)")
        input()

    finally:
        driver.quit()


if __name__ == "__main__":
    # Test with one restaurant
    url = "https://www.thuisbezorgd.nl/en/menu/babs-burritos"
    inspect_thuisbezorgd_page(url)
