"""
Menu Price Optimizer - Enhanced Multi-Site Scraper
Scrapes menu data from Thuisbezorgd and cafe websites

Features:
- Scrape entire Thuisbezorgd platform (all restaurants in a city)
- Scrape individual cafe/restaurant websites
- Automatic restaurant type classification
- Price range analysis
- Category classification
"""

from scraper_manager import ScraperManager


def main():
    """Main scraper execution"""

    # Initialize manager
    manager = ScraperManager(headless=True)

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        MENU PRICE OPTIMIZER - MULTI-SITE SCRAPER            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("\n📋 Choose scraping mode:\n")
    print("1. Discover & scrape ALL Thuisbezorgd restaurants in Maastricht")
    print("2. Scrape specific Thuisbezorgd restaurants")
    print("3. Scrape Mickey Browns (multi-page cafe)")
    print("4. Scrape custom URLs (mixed sources)")
    print("5. Full Maastricht scrape (Thuisbezorgd + cafes)")

    choice = input("\nEnter choice (1-5): ").strip()

    try:
        if choice == '1':
            # Discover and scrape all Thuisbezorgd in city
            print("\n🔍 Discovering all restaurants on Thuisbezorgd...")
            max_restaurants = input("Max restaurants to scrape (default 50): ").strip()
            max_restaurants = int(max_restaurants) if max_restaurants else 50

            manager.discover_and_scrape_thuisbezorgd(
                city='maastricht',
                max_restaurants=max_restaurants
            )

        elif choice == '2':
            # Scrape specific Thuisbezorgd URLs
            restaurant_urls = [
                "https://www.thuisbezorgd.nl/en/menu/pitology",
                "https://www.thuisbezorgd.nl/en/menu/tasty-thai-maastricht",
                "https://www.thuisbezorgd.nl/en/menu/babs-burritos",
                "https://www.thuisbezorgd.nl/en/menu/new-china-garden",
                "https://www.thuisbezorgd.nl/en/menu/pasta-corner",
            ]

            manager.scrape_multiple_urls(restaurant_urls)

        elif choice == '3':
            # Scrape Mickey Browns
            manager.scrape_mickey_browns()

        elif choice == '4':
            # Custom URLs
            print("\n📝 Enter URLs to scrape (one per line, empty line to finish):")
            urls = []
            while True:
                url = input("URL: ").strip()
                if not url:
                    break
                urls.append(url)

            if urls:
                manager.scrape_multiple_urls(urls)
            else:
                print("No URLs provided")
                return

        elif choice == '5':
            # Full Maastricht scrape
            print("\n🌍 Full Maastricht restaurant scrape!")
            print("This will scrape Thuisbezorgd + known cafes")

            # Thuisbezorgd
            manager.discover_and_scrape_thuisbezorgd(city='maastricht', max_restaurants=30)

            # Add known cafes
            cafes = [
                {
                    'url': 'https://mickeybrowns.nl/drinks-1',
                    'name': 'Mickey Browns'
                }
                # Add more cafes here
            ]

            if cafes:
                print("\n\n🍺 Now scraping local cafes...")
                for cafe in cafes:
                    manager.scrape_url(cafe['url'], cafe['name'])

        else:
            print("Invalid choice")
            return

        # Print summary
        manager.print_summary()

        # Save data
        if manager.data:
            manager.save_to_json()
            manager.save_to_csv()

            print("\n✅ All done! Data saved to:")
            print("  • scraped_menus.json")
            print("  • scraped_menus.csv")
        else:
            print("\n⚠️  No data collected")

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")

    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        manager.close_all()


if __name__ == "__main__":
    main()
