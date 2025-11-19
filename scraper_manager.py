"""
Scraper Manager
Intelligently routes URLs to the appropriate scraper
Coordinates multi-site scraping operations
"""

import pandas as pd
import json
from scrapers import ThuisbezorgdScraper, SquarespaceScraper, GenericScraper


class ScraperManager:
    """Manages multiple scrapers and coordinates scraping operations"""

    def __init__(self, headless=True):
        """Initialize scraper manager"""
        self.headless = headless
        self.scrapers = {
            'thuisbezorgd': ThuisbezorgdScraper(headless=headless),
            'squarespace': SquarespaceScraper(headless=headless),
            'generic': GenericScraper(headless=headless)
        }
        self.data = []

    def get_scraper_for_url(self, url):
        """
        Determine which scraper to use for a URL
        Returns the appropriate scraper instance
        """
        # Check each scraper in priority order
        if self.scrapers['thuisbezorgd'].can_scrape(url):
            return self.scrapers['thuisbezorgd']
        elif self.scrapers['squarespace'].can_scrape(url):
            return self.scrapers['squarespace']
        else:
            # Fall back to generic scraper
            return self.scrapers['generic']

    def scrape_url(self, url, restaurant_name=None):
        """
        Scrape a single URL using the appropriate scraper
        """
        print(f"\n{'='*60}")
        print(f"Scraping: {url}")
        print(f"{'='*60}")

        scraper = self.get_scraper_for_url(url)
        scraper_name = [k for k, v in self.scrapers.items() if v == scraper][0]
        print(f"Using: {scraper_name.upper()} scraper")

        try:
            if restaurant_name:
                result = scraper.scrape_restaurant(url, restaurant_name=restaurant_name)
            else:
                result = scraper.scrape_restaurant(url)

            if result:
                self.data.append(result)
                return result
            else:
                print(f"⚠️  No data extracted from {url}")
                return None

        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return None

    def scrape_multiple_urls(self, urls, delay=2):
        """
        Scrape multiple URLs
        urls can be a list of strings or list of dicts with 'url' and 'name' keys
        """
        print(f"\n🚀 Starting multi-site scraping of {len(urls)} URLs")

        import time

        for i, url_info in enumerate(urls, 1):
            # Handle both string URLs and dict format
            if isinstance(url_info, dict):
                url = url_info['url']
                restaurant_name = url_info.get('name', None)
            else:
                url = url_info
                restaurant_name = None

            print(f"\n[{i}/{len(urls)}]", end=" ")
            self.scrape_url(url, restaurant_name=restaurant_name)

            # Delay between requests
            if i < len(urls):
                time.sleep(delay)

        print(f"\n{'='*60}")
        print(f"✅ Scraping complete! Collected data from {len(self.data)} restaurants")
        print(f"{'='*60}")

        return self.data

    def discover_and_scrape_thuisbezorgd(self, city='maastricht', max_restaurants=None, progress_callback=None):
        """
        Discover all restaurants in a city on Thuisbezorgd and scrape them
        Set max_restaurants=None to scrape ALL restaurants (default)
        progress_callback: optional function(current, total, message) for UI updates
        """
        print(f"\n{'='*60}")
        print(f"🔍 DISCOVERING & SCRAPING THUISBEZORGD - {city.upper()}")
        print(f"{'='*60}")

        thuisbezorgd = self.scrapers['thuisbezorgd']

        # Discover restaurants
        if progress_callback:
            progress_callback(0, 100, f"Discovering restaurants in {city.title()}...")

        restaurant_urls = thuisbezorgd.discover_restaurants(city=city, max_restaurants=max_restaurants)

        if not restaurant_urls:
            print(f"⚠️  No restaurants found in {city}")
            return []

        print(f"\n📋 Found {len(restaurant_urls)} restaurants to scrape")
        print(f"{'='*60}\n")

        if progress_callback:
            progress_callback(10, 100, f"Found {len(restaurant_urls)} restaurants. Starting scraping...")

        # Scrape each restaurant
        import time
        for i, url in enumerate(restaurant_urls, 1):
            print(f"\n[{i}/{len(restaurant_urls)}] Scraping...")

            if progress_callback:
                # Progress from 10% to 90% during scraping
                progress_pct = 10 + int((i / len(restaurant_urls)) * 80)
                progress_callback(progress_pct, 100, f"Scraping restaurant {i}/{len(restaurant_urls)}...")

            result = thuisbezorgd.scrape_restaurant(url)

            if result:
                self.data.append(result)

            # Delay between requests
            if i < len(restaurant_urls):
                time.sleep(2)

        if progress_callback:
            progress_callback(90, 100, "Saving data...")

        print(f"\n{'='*60}")
        print(f"✅ Discovery complete! Scraped {len(self.data)} restaurants from {city}")
        print(f"{'='*60}")

        if progress_callback:
            progress_callback(100, 100, f"Complete! Scraped {len(self.data)} restaurants")

        return self.data

    def scrape_mickey_browns(self):
        """
        Special method to scrape Mickey Browns with all menu pages
        Example of handling multi-page menus
        """
        print(f"\n{'='*60}")
        print(f"🍺 SCRAPING MICKEY BROWNS (Multi-page menu)")
        print(f"{'='*60}")

        squarespace = self.scrapers['squarespace']
        restaurant_name = "Mickey Browns"

        # Scrape each menu page
        menu_pages = [
            ('https://mickeybrowns.nl/drinks-1', 'Drinks'),
            ('https://mickeybrowns.nl/food-1', 'Food'),
            ('https://mickeybrowns.nl/specials', 'Specials')
        ]

        all_items = []

        for url, page_name in menu_pages:
            items = squarespace.scrape_menu_page(url, restaurant_name, page_name)
            all_items.extend(items)

        # Combine into single restaurant entry
        if all_items:
            from scrapers.classifier import RestaurantClassifier

            restaurant_data = {
                'restaurant_name': restaurant_name,
                'url': 'https://mickeybrowns.nl/',
                'scraped_at': squarespace.get_base_data_structure(restaurant_name, 'https://mickeybrowns.nl/', all_items)['scraped_at'],
                'menu_items': all_items,
                'total_items': len(all_items)
            }

            restaurant_data = RestaurantClassifier.enhance_restaurant_data(restaurant_data)
            self.data.append(restaurant_data)

            print(f"\n✓ Scraped {len(all_items)} total items from Mickey Browns")
            print(f"  Types: {', '.join(restaurant_data['restaurant_types'])}")

            return restaurant_data

        return None

    def save_to_json(self, filename='scraped_menus.json'):
        """Save all scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Data saved to {filename}")

    def save_to_csv(self, filename='scraped_menus.csv'):
        """Save scraped data to CSV (flattened)"""
        rows = []
        for restaurant in self.data:
            restaurant_types = ', '.join(restaurant.get('restaurant_types', []))
            price_range = restaurant.get('price_range', 'unknown')

            for item in restaurant['menu_items']:
                rows.append({
                    'restaurant_name': restaurant['restaurant_name'],
                    'restaurant_types': restaurant_types,
                    'price_range': price_range,
                    'restaurant_url': restaurant['url'],
                    'item_name': item['name'],
                    'category': item['category'],
                    'price': item['price'],
                    'description': item.get('description', ''),
                    'scraped_at': restaurant['scraped_at']
                })

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Data saved to {filename}")

    def print_summary(self):
        """Print a summary of scraped data"""
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*60}")

        print(f"\n🏪 Total Restaurants: {len(self.data)}")

        total_items = sum(r['total_items'] for r in self.data)
        print(f"📋 Total Menu Items: {total_items}")

        # Restaurant types breakdown
        all_types = {}
        for restaurant in self.data:
            for rtype in restaurant.get('restaurant_types', []):
                all_types[rtype] = all_types.get(rtype, 0) + 1

        print(f"\n🍽️  Restaurant Types:")
        for rtype, count in sorted(all_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rtype.title()}: {count}")

        # Price ranges
        price_ranges = {}
        for restaurant in self.data:
            prange = restaurant.get('price_range', 'unknown')
            price_ranges[prange] = price_ranges.get(prange, 0) + 1

        print(f"\n💰 Price Ranges:")
        for prange, count in sorted(price_ranges.items()):
            print(f"  • {prange.title()}: {count}")

        # Individual restaurant details
        print(f"\n📍 Individual Restaurants:")
        for restaurant in self.data:
            types = ', '.join(restaurant.get('restaurant_types', []))
            price_range = restaurant.get('price_range', 'unknown')
            print(f"\n  {restaurant['restaurant_name']}")
            print(f"    Items: {restaurant['total_items']} | Types: {types} | Price: {price_range}")

        print(f"\n{'='*60}")

    def close_all(self):
        """Close all scrapers"""
        for scraper in self.scrapers.values():
            scraper.close()
        print("\n✓ All scrapers closed")
