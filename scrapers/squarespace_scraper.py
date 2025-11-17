"""
Squarespace Scraper
Scrapes menu data from Squarespace-based cafe/restaurant websites
Handles text-based menus without structured data
"""

from selenium.webdriver.common.by import By
import time
import re
from .base_scraper import BaseScraper
from .classifier import RestaurantClassifier


class SquarespaceScraper(BaseScraper):
    """Scraper for Squarespace-based restaurant sites"""

    def can_scrape(self, url):
        """Check if URL might be a Squarespace site"""
        # Squarespace sites often have certain patterns
        squarespace_indicators = ['squarespace', 'static1.squarespace']
        return any(indicator in url.lower() for indicator in squarespace_indicators)

    def scrape_restaurant(self, url, restaurant_name=None):
        """Scrape a Squarespace restaurant site"""
        if not self.driver:
            self.start_driver()

        print(f"\n📍 Scraping Squarespace site: {url}")

        try:
            self.driver.get(url)
            time.sleep(4)

            self.handle_cookie_popup()
            time.sleep(2)

            # Try to get restaurant name from title or h1
            if not restaurant_name:
                restaurant_name = self._get_restaurant_name()

            # Extract menu items
            menu_items = self._extract_menu_items_text_based()

            restaurant_data = self.get_base_data_structure(restaurant_name, url, menu_items)

            # Add classification
            restaurant_data = RestaurantClassifier.enhance_restaurant_data(restaurant_data)

            self.data.append(restaurant_data)
            print(f"✓ Scraped {len(menu_items)} items from {restaurant_name}")

            # Warn if no prices found
            items_with_prices = sum(1 for item in menu_items if item.get('price') and item['price'] > 0)
            if items_with_prices == 0:
                print("⚠️  No prices found - items extracted by name only")
            else:
                print(f"  {items_with_prices} items have prices")

            return restaurant_data

        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return None

    def _get_restaurant_name(self):
        """Extract restaurant name"""
        try:
            # Try title first
            title = self.driver.title
            if title and title != "":
                return title.split('|')[0].split('-')[0].strip()

            # Try h1
            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            if h1_elements:
                return h1_elements[0].text.strip()

            return "Cafe/Restaurant"
        except:
            return "Cafe/Restaurant"

    def _extract_menu_items_text_based(self):
        """
        Extract menu items from text-based menus
        Handles simple text lists without structured data
        """
        menu_items = []

        try:
            # Find main content area
            content_selectors = [
                "main",
                "[role='main']",
                ".content",
                "#content",
                "article",
                ".page-content"
            ]

            main_content = None
            for selector in content_selectors:
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not main_content:
                main_content = self.driver.find_element(By.TAG_NAME, "body")

            # Find categories (usually h2, h3, or strong tags)
            categories = main_content.find_elements(By.CSS_SELECTOR, "h2, h3, strong")

            current_category = "Menu"

            # Get all text content
            page_text = main_content.text

            # Split into lines
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]

            for i, line in enumerate(lines):
                # Check if it's a category header (usually all caps or has specific keywords)
                if self._is_category_header(line):
                    current_category = line
                    continue

                # Try to extract item and price from line
                item_data = self._parse_menu_line(line, current_category)
                if item_data:
                    menu_items.append(item_data)

            return menu_items

        except Exception as e:
            print(f"Error extracting menu items: {e}")
            return []

    def _is_category_header(self, text):
        """Check if text is likely a category header"""
        # Headers are usually short, all caps, or contain category keywords
        category_keywords = [
            'menu', 'breakfast', 'lunch', 'dinner', 'drinks', 'coffee',
            'food', 'starters', 'mains', 'desserts', 'sides', 'specials',
            'pancakes', 'waffles', 'sandwiches', 'burgers', 'pizza'
        ]

        text_lower = text.lower()

        # Check if it's all uppercase and short
        if text.isupper() and len(text.split()) <= 4:
            return True

        # Check if it contains category keywords
        if any(keyword in text_lower for keyword in category_keywords) and len(text.split()) <= 5:
            return True

        return False

    def _parse_menu_line(self, line, category):
        """
        Parse a menu line to extract item name and price
        Formats supported:
        - "Item Name €5.50"
        - "Item Name - €5.50"
        - "Item Name 5.50"
        - "Item Name" (no price)
        """
        # Skip if line is too short or too long
        if len(line) < 3 or len(line) > 100:
            return None

        # Skip common non-menu text
        skip_keywords = ['order', 'delivery', 'pick up', 'open', 'closed', 'hours', 'address', 'phone']
        if any(keyword in line.lower() for keyword in skip_keywords):
            return None

        # Try to find price pattern: €X.XX or just X.XX at the end
        price_pattern = r'€?\s?(\d+)[.,](\d{2})\s*$'
        price_match = re.search(price_pattern, line)

        if price_match:
            # Extract price
            price_str = f"{price_match.group(1)}.{price_match.group(2)}"
            price = float(price_str)

            # Extract item name (everything before the price)
            item_name = line[:price_match.start()].strip()
            item_name = item_name.rstrip('-').strip()

            return {
                'name': item_name,
                'category': category,
                'price': price,
                'price_raw': f"€{price_str}",
                'description': ''
            }
        else:
            # No price found - just item name
            # Only add if it looks like a menu item (not too long, not a sentence)
            if len(line.split()) <= 8 and not line.endswith('.'):
                return {
                    'name': line,
                    'category': category,
                    'price': None,
                    'price_raw': '',
                    'description': ''
                }

        return None

    def scrape_menu_page(self, url, restaurant_name, page_name="Menu"):
        """
        Scrape a specific menu page (e.g., drinks, food)
        Used for sites with multiple menu pages
        """
        if not self.driver:
            self.start_driver()

        print(f"\n📍 Scraping {page_name} page: {url}")

        try:
            self.driver.get(url)
            time.sleep(4)

            self.handle_cookie_popup()
            time.sleep(2)

            menu_items = self._extract_menu_items_text_based()

            # Add page name to category if not already there
            for item in menu_items:
                if item['category'] == "Menu":
                    item['category'] = page_name

            print(f"✓ Found {len(menu_items)} items on {page_name} page")

            return menu_items

        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return []
