"""
Base Scraper Class
Abstract base for all scrapers in the system
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, headless=True):
        """Initialize scraper with common settings"""
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
            raise

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("\n✓ WebDriver closed")

    def handle_cookie_popup(self):
        """Try to close cookie consent popup"""
        try:
            time.sleep(2)
            buttons = self.driver.find_elements("css selector", "button")
            for button in buttons[:10]:
                text = button.text.lower()
                if any(word in text for word in ['accept', 'agree', 'akkoord', 'toestaan', 'accepteren', 'ok']):
                    button.click()
                    time.sleep(1)
                    print("✓ Closed cookie popup")
                    break
        except:
            pass

    def clean_price(self, price_str):
        """Clean price string to float"""
        try:
            cleaned = price_str.lower().replace('from', '').replace('€', '').replace('eur', '').strip()
            cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except:
            return None

    @abstractmethod
    def scrape_restaurant(self, url):
        """Scrape a single restaurant - must be implemented by subclass"""
        pass

    @abstractmethod
    def can_scrape(self, url):
        """Check if this scraper can handle the given URL"""
        pass

    def get_base_data_structure(self, restaurant_name, url, menu_items):
        """Standard data structure for all scrapers"""
        return {
            'restaurant_name': restaurant_name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'menu_items': menu_items,
            'total_items': len(menu_items)
        }
