"""
Restaurant Classifier
Classifies restaurants by type, price range, and categorizes menu items
"""

import re
from typing import List, Dict


class RestaurantClassifier:
    """Classifies restaurants and menu items"""

    # Restaurant type keywords
    RESTAURANT_TYPES = {
        'burger': ['burger', 'burgers', 'smash', 'beef', 'patty'],
        'pizza': ['pizza', 'pizzeria', 'napoli', 'margherita'],
        'asian': ['asian', 'chinese', 'thai', 'sushi', 'wok', 'noodles', 'ramen', 'dim sum', 'pho'],
        'indian': ['indian', 'curry', 'tandoori', 'biryani', 'naan'],
        'mexican': ['mexican', 'burrito', 'taco', 'quesadilla', 'nachos', 'tex-mex'],
        'kebab': ['kebab', 'doner', 'shawarma', 'gyros'],
        'fries': ['fries', 'friet', 'snackbar', 'snack'],
        'italian': ['italian', 'pasta', 'risotto', 'lasagna', 'carbonara'],
        'breakfast': ['breakfast', 'pancake', 'waffle', 'brunch', 'eggs'],
        'cafe': ['cafe', 'coffee', 'cappuccino', 'latte', 'espresso'],
        'seafood': ['seafood', 'fish', 'salmon', 'shrimp', 'lobster'],
        'vegetarian': ['vegetarian', 'vegan', 'plant-based', 'veggie'],
        'bbq': ['bbq', 'barbecue', 'grill', 'grilled', 'ribs'],
        'sandwich': ['sandwich', 'sub', 'hoagie', 'panini'],
        'dessert': ['dessert', 'ice cream', 'gelato', 'bakery', 'pastry']
    }

    # Menu item categories
    ITEM_CATEGORIES = {
        'starters': ['starter', 'appetizer', 'voorgerecht', 'snack', 'finger food'],
        'mains': ['main', 'hoofdgerecht', 'entree', 'dinner', 'lunch'],
        'sides': ['side', 'bijgerecht', 'fries', 'salad'],
        'drinks': ['drink', 'beverage', 'soda', 'juice', 'water', 'coffee', 'tea'],
        'desserts': ['dessert', 'sweet', 'nagerecht', 'ice cream', 'cake'],
        'breakfast': ['breakfast', 'ontbijt', 'pancake', 'waffle', 'eggs'],
        'burgers': ['burger'],
        'pizza': ['pizza'],
        'pasta': ['pasta', 'spaghetti', 'penne', 'linguine'],
        'salads': ['salad', 'salade'],
        'wraps': ['wrap', 'burrito', 'quesadilla'],
        'bowls': ['bowl', 'poke'],
        'soups': ['soup', 'soep']
    }

    @staticmethod
    def classify_restaurant_type(restaurant_name: str, menu_items: List[Dict]) -> List[str]:
        """
        Classify restaurant type based on name and menu items
        Returns list of types (can be multiple)
        """
        types = []
        restaurant_name_lower = restaurant_name.lower()

        # Check restaurant name
        for resto_type, keywords in RestaurantClassifier.RESTAURANT_TYPES.items():
            for keyword in keywords:
                if keyword in restaurant_name_lower:
                    if resto_type not in types:
                        types.append(resto_type)

        # Check menu items
        menu_text = ' '.join([
            f"{item.get('name', '')} {item.get('description', '')} {item.get('category', '')}"
            for item in menu_items
        ]).lower()

        for resto_type, keywords in RestaurantClassifier.RESTAURANT_TYPES.items():
            keyword_count = sum(1 for keyword in keywords if keyword in menu_text)
            # If type appears frequently in menu, add it
            if keyword_count >= 3 and resto_type not in types:
                types.append(resto_type)

        # Default to 'restaurant' if no specific type found
        if not types:
            types.append('restaurant')

        return types

    @staticmethod
    def classify_price_range(menu_items: List[Dict]) -> Dict:
        """
        Classify price range based on average menu prices
        Returns: {
            'range': 'budget'|'moderate'|'premium'|'luxury',
            'avg_price': float,
            'min_price': float,
            'max_price': float
        }
        """
        prices = [item['price'] for item in menu_items if item.get('price') and item['price'] > 0]

        if not prices:
            return {
                'range': 'unknown',
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0
            }

        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        # Price range classification (adjusted for European restaurant prices)
        if avg_price < 8:
            price_range = 'budget'
        elif avg_price < 15:
            price_range = 'moderate'
        elif avg_price < 25:
            price_range = 'premium'
        else:
            price_range = 'luxury'

        return {
            'range': price_range,
            'avg_price': round(avg_price, 2),
            'min_price': round(min_price, 2),
            'max_price': round(max_price, 2)
        }

    @staticmethod
    def categorize_menu_item(item_name: str, existing_category: str = None) -> str:
        """
        Categorize a menu item based on its name
        Uses existing category if available and valid
        """
        # If existing category is good, use it
        if existing_category and existing_category.strip():
            return existing_category

        item_name_lower = item_name.lower()

        # Check against category keywords
        for category, keywords in RestaurantClassifier.ITEM_CATEGORIES.items():
            for keyword in keywords:
                if keyword in item_name_lower:
                    return category.title()

        return 'Other'

    @staticmethod
    def enhance_restaurant_data(restaurant_data: Dict) -> Dict:
        """
        Add classification data to restaurant data structure
        """
        menu_items = restaurant_data.get('menu_items', [])
        restaurant_name = restaurant_data.get('restaurant_name', '')

        # Classify restaurant types
        restaurant_types = RestaurantClassifier.classify_restaurant_type(
            restaurant_name, menu_items
        )

        # Classify price range
        price_info = RestaurantClassifier.classify_price_range(menu_items)

        # Enhance menu items with better categories
        enhanced_items = []
        for item in menu_items:
            item_copy = item.copy()
            item_copy['category'] = RestaurantClassifier.categorize_menu_item(
                item.get('name', ''),
                item.get('category', '')
            )
            enhanced_items.append(item_copy)

        # Add classification data
        restaurant_data['restaurant_types'] = restaurant_types
        restaurant_data['price_range'] = price_info['range']
        restaurant_data['price_info'] = price_info
        restaurant_data['menu_items'] = enhanced_items

        return restaurant_data
