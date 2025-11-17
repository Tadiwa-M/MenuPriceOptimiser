# Menu Price Optimizer 💰

Data-driven pricing tool for cafes and restaurants in Maastricht (and beyond!).

## Features

### Multi-Site Scraping System
- **Thuisbezorgd Discovery**: Automatically discover and scrape ALL restaurants in a city
- **Cafe Website Scraping**: Support for Squarespace and generic cafe websites
- **Intelligent Routing**: Automatically selects the right scraper for each URL
- **Multi-page Menu Support**: Handle restaurants with separate food/drinks pages

### Restaurant Classification
- **Automatic Type Detection**: Classifies restaurants (burger, asian, pizza, cafe, etc.)
- **Price Range Analysis**: Categorizes as budget, moderate, premium, or luxury
- **Menu Categorization**: Intelligently categorizes menu items

### Analysis Dashboard
- **Market Overview**: Compare prices across all restaurants
- **Filter by Type**: View data by restaurant type (burgers, asian, etc.)
- **Filter by Price Range**: Budget, moderate, premium, luxury
- **Competitor Analysis**: Detailed price comparisons
- **Profit Calculator**: Calculate margins and pricing scenarios
- **AI Recommendations**: Get pricing insights from Claude AI

## Installation

### Prerequisites
- Python 3.8+
- Chrome browser (for web scraping)
- Anthropic API key (optional, for AI recommendations)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Tadiwa-M/MenuPriceOptimiser.git
cd MenuPriceOptimiser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up API key for AI features:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### Scraping Data

Run the interactive scraper:
```bash
python scraper_new.py
```

Choose from:
1. **Discover ALL Thuisbezorgd restaurants** in Maastricht
2. **Scrape specific Thuisbezorgd URLs**
3. **Scrape Mickey Browns** (multi-page cafe example)
4. **Scrape custom URLs** (mixed sources)
5. **Full Maastricht scrape** (Thuisbezorgd + cafes)

### Viewing Results

Launch the dashboard:
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## Project Structure

```
MenuPriceOptimiser/
├── scrapers/
│   ├── base_scraper.py          # Abstract base class
│   ├── classifier.py            # Restaurant/menu classification
│   ├── thuisbezorgd_scraper.py  # Thuisbezorgd scraper
│   ├── squarespace_scraper.py   # Squarespace cafe scraper
│   └── generic_scraper.py       # Generic website scraper
├── scraper_manager.py           # Coordinates all scrapers
├── scraper_new.py               # Interactive scraper CLI
├── app.py                       # Streamlit dashboard
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Adding New Scrapers

To add support for a new website type:

1. Create a new scraper in `scrapers/` that extends `BaseScraper`
2. Implement `can_scrape(url)` and `scrape_restaurant(url)` methods
3. Add to `ScraperManager` in `scraper_manager.py`

Example:
```python
from .base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def can_scrape(self, url):
        return 'mywebsite.com' in url

    def scrape_restaurant(self, url):
        # Your scraping logic here
        pass
```

## Restaurant Type Classification

The system automatically classifies restaurants into types:
- Burger
- Pizza
- Asian (Chinese, Thai, Sushi, etc.)
- Indian
- Mexican
- Kebab
- Italian
- Breakfast/Cafe
- Seafood
- BBQ
- And more...

## Price Range Classification

Restaurants are classified by average menu price:
- **Budget**: < €8 average
- **Moderate**: €8-15 average
- **Premium**: €15-25 average
- **Luxury**: > €25 average

## Data Output

Scraped data is saved in two formats:

**scraped_menus.json**: Complete hierarchical data
```json
{
  "restaurant_name": "Example Restaurant",
  "restaurant_types": ["burger", "american"],
  "price_range": "moderate",
  "menu_items": [...]
}
```

**scraped_menus.csv**: Flattened for analysis
| restaurant_name | restaurant_types | price_range | item_name | category | price |
|-----------------|------------------|-------------|-----------|----------|-------|

## Advanced Features

### Multi-Page Scraping

For restaurants with multiple menu pages (drinks, food, specials):

```python
from scraper_manager import ScraperManager

manager = ScraperManager()
manager.scrape_mickey_browns()  # Scrapes all 3 pages
```

### Custom URL Lists

```python
urls = [
    {'url': 'https://example.com/menu', 'name': 'Restaurant Name'},
    {'url': 'https://another.com', 'name': 'Another Place'}
]
manager.scrape_multiple_urls(urls)
```

## Troubleshooting

### Chrome Driver Issues
If you get WebDriver errors, the system will automatically download the correct ChromeDriver version.

### No Data Found
- Check if the website structure has changed
- Try running in non-headless mode: `ScraperManager(headless=False)`
- Some websites require manual price input (they don't display prices online)

### Slow Scraping
- The scraper includes delays to be respectful to servers
- Expect 2-3 seconds per restaurant
- For 50 restaurants, allow ~3-5 minutes

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - Feel free to use for your projects!

## Credits

Built with:
- [Selenium](https://www.selenium.dev/) - Web scraping
- [Streamlit](https://streamlit.io/) - Dashboard
- [Claude AI](https://www.anthropic.com/) - AI recommendations
- [Plotly](https://plotly.com/) - Visualizations

---

**Questions?** Open an issue on GitHub!
