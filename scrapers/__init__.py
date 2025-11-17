"""
Menu Price Optimizer - Scraper Package
Modular web scraping system for restaurant menus
"""

from .base_scraper import BaseScraper
from .classifier import RestaurantClassifier
from .thuisbezorgd_scraper import ThuisbezorgdScraper
from .squarespace_scraper import SquarespaceScraper
from .generic_scraper import GenericScraper

__all__ = [
    'BaseScraper',
    'RestaurantClassifier',
    'ThuisbezorgdScraper',
    'SquarespaceScraper',
    'GenericScraper'
]
