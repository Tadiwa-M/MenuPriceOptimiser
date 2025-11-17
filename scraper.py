"""
Thuisbezorgd Menu Scraper - Phase 1
Restaurant Menu Optimizer Project

This scraper extracts menu data from Thuisbezorgd restaurant pages.
Uses Selenium for JavaScript-rendered content.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
from datetime import datetime


class ThuisbezorgdScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome WebDriver"""
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = None
        self.data = []

    def start_driver(self):
        """Start the Chrome WebDriver"""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            print("✓ WebDriver started successfully")
        except Exception as e:
            print(f"✗ Error starting WebDriver: {e}")
            print("\nMake sure you have Chrome browser installed")
            raise

    def scrape_restaurant(self, url):
        """Scrape a single restaurant's menu"""
        if not self.driver:
            self.start_driver()

        print(f"\n📍 Scraping: {url}")

        try:
            # Load the page
            self.driver.get(url)
            time.sleep(4)  # Wait for JavaScript to load

            # Try to close cookie popup
            self._handle_cookie_popup()

            # Try to close any "restaurant closed" popups
            self._handle_closed_popup()

            # Wait extra time for content to fully render
            time.sleep(2)

            # Extract restaurant name
            restaurant_name = self._get_restaurant_name()

            # Extract menu items
            menu_items = self._extract_menu_items()

            # Store data
            restaurant_data = {
                'restaurant_name': restaurant_name,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'menu_items': menu_items,
                'total_items': len(menu_items)
            }

            self.data.append(restaurant_data)
            print(f"✓ Scraped {len(menu_items)} items from {restaurant_name}")

            return restaurant_data

        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return None

    def _handle_cookie_popup(self):
        """Try to close cookie consent popup"""
        try:
            # Wait a bit for popup to appear
            time.sleep(2)

            # Look for accept button
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            for button in buttons[:10]:  # Check first 10 buttons
                text = button.text.lower()
                if any(word in text for word in ['accept', 'agree', 'akkoord', 'toestaan', 'accepteren']):
                    button.click()
                    time.sleep(1)
                    print("✓ Closed cookie popup")
                    break
        except:
            pass  # No popup or couldn't close it

    def _handle_closed_popup(self):
        """Try to close 'restaurant closed' popup"""
        try:
            # Look for buttons that might close the popup
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            for button in buttons[:15]:
                text = button.text.lower()
                if any(word in text for word in ['order for later', 'x', 'close', 'sluiten']):
                    # Click the X or close button, not "Order for later"
                    if 'x' in text or 'close' in text or 'sluiten' in text or button.get_attribute('aria-label') == 'Close':
                        button.click()
                        time.sleep(1)
                        print("✓ Closed restaurant popup")
                        break
        except:
            pass

    def _get_restaurant_name(self):
        """Extract restaurant name from page"""
        try:
            # Try multiple possible selectors
            selectors = [
                "h1",
                "[data-testid='restaurant-name']",
                ".restaurant-name",
                "header h1"
            ]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = element.text.strip()
                    if name:
                        return name
                except:
                    continue

            return "Unknown Restaurant"

        except Exception as e:
            print(f"Warning: Could not extract restaurant name: {e}")
            return "Unknown Restaurant"

    def _extract_menu_items(self):
        """Extract all menu items with prices"""
        menu_items = []

        try:
            # Wait for menu to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-qa*='category']"))
            )

            # Find all category sections
            categories = self.driver.find_elements(By.CSS_SELECTOR, "section[data-qa*='category']")

            if not categories:
                print("Warning: No menu categories found")
                return []

            print(f"Found {len(categories)} menu categories")

            # Extract items from each category
            for category in categories:
                try:
                    # Get category name
                    category_name = ""
                    try:
                        category_heading = category.find_element(By.CSS_SELECTOR, "h2")
                        category_name = category_heading.text.strip()
                    except:
                        pass

                    # Try Method 1: Find items in <li> tags (BABS format)
                    li_items = category.find_elements(By.CSS_SELECTOR, "li[class*='item-list']")

                    if li_items:
                        # Process <li> items
                        for li in li_items:
                            try:
                                # Wait for the li element to have text content
                                time.sleep(0.2)  # Small delay for JS to populate text

                                # Find name using get_attribute('textContent') instead of .text
                                name = ""
                                for selector in ["h3", "strong", "[class*='name']"]:
                                    try:
                                        name_elem = li.find_element(By.CSS_SELECTOR, selector)
                                        # Try both .text and textContent
                                        name = name_elem.text.strip() or name_elem.get_attribute('textContent').strip()
                                        if name:
                                            break
                                    except:
                                        continue

                                # Find price
                                price = ""
                                for selector in ["[data-qa*='price']", "[class*='price']", "span"]:
                                    try:
                                        price_elem = li.find_element(By.CSS_SELECTOR, selector)
                                        price = price_elem.text.strip() or price_elem.get_attribute('textContent').strip()
                                        if price and ('€' in price or 'from' in price.lower()):
                                            break
                                    except:
                                        continue

                                # Find description
                                description = ""
                                try:
                                    desc_elem = li.find_element(By.CSS_SELECTOR, "p[class*='description'], div[class*='description']")
                                    description = desc_elem.text.strip() or desc_elem.get_attribute('textContent').strip()
                                except:
                                    pass

                                if name and price:
                                    menu_items.append({
                                        'name': name,
                                        'category': category_name,
                                        'price': self._clean_price(price),
                                        'price_raw': price,
                                        'description': description
                                    })
                            except Exception as e:
                                continue

                    else:
                        # Method 2: Find all h3 elements (Pitology/Tasty Thai format)
                        item_elements = category.find_elements(By.CSS_SELECTOR, "h3")

                        for item_elem in item_elements:
                            try:
                                # Get the parent container to find associated price
                                parent = item_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@data-qa, 'item')]")

                                # Extract item name
                                name = item_elem.text.strip()

                                # Extract price
                                price = ""
                                try:
                                    price_elem = parent.find_element(By.CSS_SELECTOR, "[data-qa*='price']")
                                    price = price_elem.text.strip()
                                except:
                                    try:
                                        price_elem = parent.find_element(By.CSS_SELECTOR, "[class*='price']")
                                        price = price_elem.text.strip()
                                    except:
                                        pass

                                # Extract description (skip if it's the category item count)
                                description = ""
                                try:
                                    desc_elem = parent.find_element(By.CSS_SELECTOR, "p")
                                    desc_text = desc_elem.text.strip()
                                    # Filter out "X items" text
                                    if not desc_text.endswith("items") and not desc_text.endswith("item"):
                                        description = desc_text
                                except:
                                    pass

                                if name and price:
                                    menu_items.append({
                                        'name': name,
                                        'category': category_name,
                                        'price': self._clean_price(price),
                                        'price_raw': price,
                                        'description': description
                                    })

                            except Exception as e:
                                continue

                except Exception as e:
                    continue

            return menu_items

        except Exception as e:
            print(f"Error extracting menu items: {e}")
            return []

    def _extract_text(self, parent_element, selectors):
        """Try multiple selectors to extract text"""
        for selector in selectors:
            try:
                element = parent_element.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        return ""

    def _clean_price(self, price_str):
        """Clean price string to float"""
        try:
            # Remove "from", currency symbols, and convert to float
            # Handle formats like "from € 19,95" or "€ 10.50"
            cleaned = price_str.lower().replace('from', '').replace('€', '').replace('eur', '').strip()
            # Replace comma with dot for decimal
            cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except:
            return None

    def scrape_multiple_restaurants(self, urls):
        """Scrape multiple restaurants"""
        print(f"\n🚀 Starting scraping of {len(urls)} restaurants...\n")

        for url in urls:
            self.scrape_restaurant(url)
            time.sleep(2)  # Be nice to the server

        print(f"\n✓ Completed scraping {len(self.data)} restaurants")

    def save_to_json(self, filename='scraped_menus.json'):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Data saved to {filename}")

    def save_to_csv(self, filename='scraped_menus.csv'):
        """Save scraped data to CSV (flattened)"""
        rows = []
        for restaurant in self.data:
            for item in restaurant['menu_items']:
                rows.append({
                    'restaurant_name': restaurant['restaurant_name'],
                    'restaurant_url': restaurant['url'],
                    'item_name': item['name'],
                    'price': item['price'],
                    'description': item.get('description', ''),
                    'scraped_at': restaurant['scraped_at']
                })

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Data saved to {filename}")

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("\n✓ WebDriver closed")


# Main execution
if __name__ == "__main__":
    # Maastricht Restaurant URLs
    restaurant_urls = [
        # Already tested
        "https://www.thuisbezorgd.nl/en/menu/pitology",
        "https://www.thuisbezorgd.nl/en/menu/tasty-thai-maastricht",
        "https://www.thuisbezorgd.nl/en/menu/babs-burritos",

        # Popular restaurants
        "https://www.thuisbezorgd.nl/en/menu/new-china-garden",
        "https://www.thuisbezorgd.nl/en/menu/chinees-restaurant-chi",
        "https://www.thuisbezorgd.nl/en/menu/futago-food-house",
        "https://www.thuisbezorgd.nl/en/menu/pasta-corner",
        "https://www.thuisbezorgd.nl/en/menu/seven-spices-maastricht",
        "https://www.thuisbezorgd.nl/en/menu/new-york-pizza-maastricht-brusselse-poort",
        "https://www.thuisbezorgd.nl/en/menu/patty-n-bun",
        "https://www.thuisbezorgd.nl/en/menu/surfside-maastricht",
        "https://www.thuisbezorgd.nl/en/menu/eethuis-zam-zam",
        "https://www.thuisbezorgd.nl/en/menu/pizzeria-napoli-maastricht",
        "https://www.thuisbezorgd.nl/en/menu/kebab-point-maastricht",
    ]

    # Create scraper instance
    scraper = ThuisbezorgdScraper(headless=True)  # Run in background (faster)

    try:
        # Scrape restaurants
        scraper.scrape_multiple_restaurants(restaurant_urls)

        # Save results
        scraper.save_to_json()
        scraper.save_to_csv()

        # Print summary
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        for restaurant in scraper.data:
            print(f"\n{restaurant['restaurant_name']}")
            print(f"  Items found: {restaurant['total_items']}")
            print(f"  URL: {restaurant['url']}")

    finally:
        scraper.close()