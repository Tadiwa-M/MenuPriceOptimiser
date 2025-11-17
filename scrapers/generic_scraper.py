"""
Generic Scraper
Attempts to scrape menu data from any restaurant website
Uses common patterns and heuristics
"""

from selenium.webdriver.common.by import By
import time
import re
from .base_scraper import BaseScraper
from .classifier import RestaurantClassifier


class GenericScraper(BaseScraper):
    """Generic scraper that tries common menu patterns"""

    def can_scrape(self, url):
        """Can attempt any URL"""
        return True

    def scrape_restaurant(self, url, restaurant_name=None):
        """Scrape a generic restaurant website"""
        if not self.driver:
            self.start_driver()

        print(f"\n📍 Attempting generic scrape: {url}")

        try:
            self.driver.get(url)
            time.sleep(4)

            self.handle_cookie_popup()
            time.sleep(2)

            if not restaurant_name:
                restaurant_name = self._get_restaurant_name()

            # Try multiple extraction methods
            menu_items = []

            # Method 1: Structured menu items
            structured_items = self._extract_structured_items()
            if structured_items:
                menu_items.extend(structured_items)
                print(f"  Found {len(structured_items)} items using structured method")

            # Method 2: Text-based extraction
            if len(menu_items) < 5:  # Only try if structured method didn't find much
                text_items = self._extract_text_based_items()
                if text_items:
                    menu_items.extend(text_items)
                    print(f"  Found {len(text_items)} items using text-based method")

            if not menu_items:
                print("⚠️  No menu items found with generic scraper")
                return None

            restaurant_data = self.get_base_data_structure(restaurant_name, url, menu_items)
            restaurant_data = RestaurantClassifier.enhance_restaurant_data(restaurant_data)

            self.data.append(restaurant_data)
            print(f"✓ Scraped {len(menu_items)} items from {restaurant_name}")

            return restaurant_data

        except Exception as e:
            print(f"✗ Error with generic scraper on {url}: {e}")
            return None

    def _get_restaurant_name(self):
        """Extract restaurant name"""
        try:
            # Try multiple methods
            # 1. Page title
            title = self.driver.title
            if title:
                clean_title = title.split('|')[0].split('-')[0].strip()
                if clean_title and len(clean_title) < 50:
                    return clean_title

            # 2. H1 tag
            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            if h1_elements:
                h1_text = h1_elements[0].text.strip()
                if h1_text and len(h1_text) < 50:
                    return h1_text

            # 3. Site name from meta tags
            try:
                meta = self.driver.find_element(By.CSS_SELECTOR, "meta[property='og:site_name']")
                site_name = meta.get_attribute("content")
                if site_name:
                    return site_name
            except:
                pass

            return "Restaurant"

        except:
            return "Restaurant"

    def _extract_structured_items(self):
        """
        Try to extract items from structured HTML
        Looks for common menu item patterns
        """
        menu_items = []

        # Common selectors for menu items
        item_selectors = [
            ".menu-item",
            "[class*='menu-item']",
            "[class*='product']",
            ".dish",
            "[class*='dish']",
            "li[class*='item']",
            "[class*='food-item']"
        ]

        for selector in item_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                if len(elements) > 3:  # Only consider if we find multiple items
                    print(f"  Trying selector: {selector} ({len(elements)} elements)")

                    for element in elements:
                        try:
                            # Extract name
                            name = ""
                            name_selectors = ["h3", "h4", ".name", "[class*='name']", "strong", ".title"]
                            for name_sel in name_selectors:
                                try:
                                    name_elem = element.find_element(By.CSS_SELECTOR, name_sel)
                                    name = name_elem.text.strip()
                                    if name:
                                        break
                                except:
                                    continue

                            if not name:
                                name = element.text.strip().split('\n')[0]

                            # Extract price
                            price_pattern = r'€?\s?(\d+)[.,](\d{2})'
                            text = element.text
                            price_match = re.search(price_pattern, text)

                            price = None
                            price_raw = ""
                            if price_match:
                                price_str = f"{price_match.group(1)}.{price_match.group(2)}"
                                price = float(price_str)
                                price_raw = f"€{price_str}"

                            # Extract description
                            description = ""
                            desc_selectors = ["p", ".description", "[class*='description']"]
                            for desc_sel in desc_selectors:
                                try:
                                    desc_elem = element.find_element(By.CSS_SELECTOR, desc_sel)
                                    description = desc_elem.text.strip()
                                    if description and description != name:
                                        break
                                except:
                                    continue

                            if name and len(name) > 2:
                                menu_items.append({
                                    'name': name,
                                    'category': 'Menu',
                                    'price': price,
                                    'price_raw': price_raw,
                                    'description': description
                                })

                        except:
                            continue

                    if menu_items:
                        return menu_items  # Return if we found items

            except:
                continue

        return menu_items

    def _extract_text_based_items(self):
        """
        Extract items from plain text when structure is minimal
        Similar to Squarespace scraper
        """
        menu_items = []

        try:
            # Find main content
            content_selectors = ["main", "[role='main']", ".content", "#content", "article"]

            main_content = None
            for selector in content_selectors:
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not main_content:
                main_content = self.driver.find_element(By.TAG_NAME, "body")

            # Get text and split into lines
            page_text = main_content.text
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]

            current_category = "Menu"

            for line in lines:
                # Check for category
                if self._looks_like_category(line):
                    current_category = line
                    continue

                # Parse menu line
                item = self._parse_line(line, current_category)
                if item:
                    menu_items.append(item)

            return menu_items

        except Exception as e:
            print(f"  Error in text-based extraction: {e}")
            return []

    def _looks_like_category(self, text):
        """Check if line looks like a category header"""
        if len(text) > 50:
            return False

        category_words = [
            'menu', 'breakfast', 'lunch', 'dinner', 'drinks', 'appetizers',
            'starters', 'mains', 'desserts', 'sides', 'specials'
        ]

        text_lower = text.lower()
        return any(word in text_lower for word in category_words)

    def _parse_line(self, line, category):
        """Parse a line for menu item and price"""
        if len(line) < 3 or len(line) > 100:
            return None

        # Look for price
        price_pattern = r'€?\s?(\d+)[.,](\d{2})\s*$'
        price_match = re.search(price_pattern, line)

        if price_match:
            price_str = f"{price_match.group(1)}.{price_match.group(2)}"
            price = float(price_str)
            item_name = line[:price_match.start()].strip().rstrip('-').strip()

            return {
                'name': item_name,
                'category': category,
                'price': price,
                'price_raw': f"€{price_str}",
                'description': ''
            }

        return None
