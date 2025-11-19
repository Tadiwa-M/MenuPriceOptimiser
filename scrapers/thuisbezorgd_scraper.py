"""
Thuisbezorgd Scraper - Enhanced
Scrapes menu data from Thuisbezorgd.nl restaurant pages
Includes restaurant discovery by city
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper
from .classifier import RestaurantClassifier


class ThuisbezorgdScraper(BaseScraper):
    """Enhanced Thuisbezorgd scraper with city-wide discovery"""

    def can_scrape(self, url):
        """Check if URL is from Thuisbezorgd"""
        return 'thuisbezorgd.nl' in url.lower()

    def discover_restaurants(self, city='maastricht', max_restaurants=None):
        """
        Discover restaurants in a city from Thuisbezorgd
        Returns list of restaurant URLs
        Set max_restaurants=None to get ALL restaurants (default)
        """
        if not self.driver:
            self.start_driver()

        print(f"\n🔍 Discovering restaurants in {city.title()}...")
        if max_restaurants:
            print(f"   Limiting to {max_restaurants} restaurants")
        else:
            print(f"   Scraping ALL restaurants (no limit)")

        try:
            # Navigate to city page
            url = f"https://www.thuisbezorgd.nl/en/order-takeaway-{city.lower()}"
            self.driver.get(url)
            time.sleep(5)

            # Handle cookie popup
            self.handle_cookie_popup()
            time.sleep(2)

            # Scroll to load ALL restaurants
            # Keep scrolling until no new restaurants are found
            restaurant_links = set()
            previous_count = 0
            no_change_count = 0
            scroll_iteration = 0

            print("   Scrolling to load all restaurants...")

            while True:
                scroll_iteration += 1

                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for content to load

                # Try multiple selectors for restaurant links
                selectors = [
                    "a[href*='/menu/']",
                    "a[data-qa*='restaurant']",
                    "[class*='restaurant'] a"
                ]

                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            href = element.get_attribute('href')
                            if href and '/menu/' in href and 'thuisbezorgd.nl' in href:
                                restaurant_links.add(href)
                    except:
                        continue

                current_count = len(restaurant_links)
                print(f"   Scroll {scroll_iteration}: Found {current_count} restaurants", end="\r")

                # Check if we found new restaurants
                if current_count == previous_count:
                    no_change_count += 1
                    # If no new restaurants found after 3 scrolls, we're done
                    if no_change_count >= 3:
                        print(f"\n   ✓ Reached end of results after {scroll_iteration} scrolls")
                        break
                else:
                    no_change_count = 0  # Reset counter if we found new restaurants

                previous_count = current_count

                # Safety limit to prevent infinite scrolling
                if scroll_iteration >= 100:
                    print(f"\n   ⚠ Reached safety limit of 100 scrolls")
                    break

            # Convert to list and apply limit if specified
            restaurant_urls = list(restaurant_links)

            if max_restaurants:
                restaurant_urls = restaurant_urls[:max_restaurants]
                print(f"\n✓ Found {len(restaurant_urls)} restaurants (limited to {max_restaurants})")
            else:
                print(f"\n✓ Found {len(restaurant_urls)} restaurants (ALL)")

            return restaurant_urls

        except Exception as e:
            print(f"✗ Error discovering restaurants: {e}")
            return []

    def scrape_restaurant(self, url):
        """Scrape a single restaurant's menu"""
        if not self.driver:
            self.start_driver()

        print(f"\n📍 Scraping: {url}")

        try:
            self.driver.get(url)
            time.sleep(4)

            self.handle_cookie_popup()
            self._handle_closed_popup()
            time.sleep(2)

            restaurant_name = self._get_restaurant_name()
            menu_items = self._extract_menu_items()

            restaurant_data = self.get_base_data_structure(restaurant_name, url, menu_items)

            # Add classification data
            restaurant_data = RestaurantClassifier.enhance_restaurant_data(restaurant_data)

            self.data.append(restaurant_data)
            print(f"✓ Scraped {len(menu_items)} items from {restaurant_name}")
            print(f"  Types: {', '.join(restaurant_data['restaurant_types'])}")
            print(f"  Price Range: {restaurant_data['price_range']}")

            return restaurant_data

        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return None

    def _handle_closed_popup(self):
        """Try to close 'restaurant closed' popup"""
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            for button in buttons[:15]:
                text = button.text.lower()
                if any(word in text for word in ['x', 'close', 'sluiten']) or button.get_attribute('aria-label') == 'Close':
                    button.click()
                    time.sleep(1)
                    print("✓ Closed restaurant popup")
                    break
        except:
            pass

    def _get_restaurant_name(self):
        """Extract restaurant name from page"""
        try:
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

            categories = self.driver.find_elements(By.CSS_SELECTOR, "section[data-qa*='category']")

            if not categories:
                print("Warning: No menu categories found")
                return []

            print(f"Found {len(categories)} menu categories")

            for category in categories:
                try:
                    # Get category name
                    category_name = ""
                    try:
                        category_heading = category.find_element(By.CSS_SELECTOR, "h2")
                        category_name = category_heading.text.strip()
                    except:
                        pass

                    # Method 1: Find items in <li> tags (BABS format)
                    li_items = category.find_elements(By.CSS_SELECTOR, "li[class*='item-list']")

                    if li_items:
                        for li in li_items:
                            try:
                                time.sleep(0.2)

                                # Find name
                                name = ""
                                for selector in ["h3", "strong", "[class*='name']"]:
                                    try:
                                        name_elem = li.find_element(By.CSS_SELECTOR, selector)
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
                                        'price': self.clean_price(price),
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
                                parent = item_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@data-qa, 'item')]")

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

                                # Extract description
                                description = ""
                                try:
                                    desc_elem = parent.find_element(By.CSS_SELECTOR, "p")
                                    desc_text = desc_elem.text.strip()
                                    if not desc_text.endswith("items") and not desc_text.endswith("item"):
                                        description = desc_text
                                except:
                                    pass

                                if name and price:
                                    menu_items.append({
                                        'name': name,
                                        'category': category_name,
                                        'price': self.clean_price(price),
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

    def scrape_multiple_restaurants(self, urls):
        """Scrape multiple restaurants"""
        print(f"\n🚀 Starting scraping of {len(urls)} restaurants...\n")

        for url in urls:
            self.scrape_restaurant(url)
            time.sleep(2)

        print(f"\n✓ Completed scraping {len(self.data)} restaurants")
