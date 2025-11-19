"""
Menu Price Optimizer - Streamlit Dashboard
MVP for cafes and restaurants to optimize their pricing
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import anthropic
import os
import sys
from pathlib import Path

# Add scrapers to path
sys.path.insert(0, str(Path(__file__).parent))

# Import scraper manager
from scraper_manager import ScraperManager

# Page config
st.set_page_config(
    page_title="Menu Price Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Clean, Spotify-inspired design
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #121212;
    }

    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1rem;
        color: #B3B3B3;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* Tab styling - Enhanced smooth transitions */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #282828;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 0;
        color: #B3B3B3;
        font-size: 14px;
        font-weight: 600;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF;
        background-color: #1A1A1A;
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #FFFFFF;
        border-bottom: 3px solid #1DB954;
    }

    /* Category cards */
    .category-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #282828;
        cursor: pointer;
    }
    .category-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(29, 185, 84, 0.3);
        border-color: #1DB954;
    }
    .category-name {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .category-stats {
        color: #B3B3B3;
        font-size: 0.875rem;
    }
    .category-price {
        color: #1DB954;
        font-weight: 700;
        font-size: 1.25rem;
        margin-top: 0.5rem;
    }
    
    /* Metric styling */
    div[data-testid="metric-container"] {
        background-color: #181818;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #282828;
    }
    div[data-testid="metric-container"] label {
        color: #B3B3B3 !important;
        font-size: 0.875rem;
        font-weight: 600;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    /* Card/container styling */
    .element-container {
        background-color: #181818;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #181818;
        border-radius: 8px;
    }
    
    /* Input styling */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border: 1px solid #3E3E3E !important;
        border-radius: 4px !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #B3B3B3 !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #1DB954;
        color: #FFFFFF;
        border: none;
        border-radius: 24px;
        padding: 12px 32px;
        font-weight: 700;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #1ED760;
        transform: scale(1.02);
    }
    
    /* Alert/info boxes */
    .stAlert {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        color: #FFFFFF;
    }
    
    /* Markdown headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Text */
    p, span, div {
        color: #B3B3B3;
    }
    
    /* Slider */
    .stSlider {
        padding-top: 1rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #181818 !important;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Multiselect styling */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1DB954 !important;
        color: #FFFFFF !important;
    }

    /* Improved spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Section headers */
    .stMarkdown h4 {
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #282828;
    }

    /* Better info boxes */
    .stAlert > div {
        padding: 1rem !important;
    }

    /* Smooth animations for all interactive elements */
    button, input, select, .stDataFrame, .category-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load scraped data
@st.cache_data
def load_data():
    with open('scraped_menus.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_restaurants = len(data)
    
    # Convert to DataFrame
    rows = []
    for restaurant in data:
        restaurant_types = ', '.join(restaurant.get('restaurant_types', ['restaurant']))
        price_range = restaurant.get('price_range', 'unknown')

        for item in restaurant['menu_items']:
            rows.append({
                'restaurant': restaurant['restaurant_name'],
                'restaurant_types': restaurant_types,
                'price_range': price_range,
                'item_name': item['name'],
                'category': item['category'],
                'price': item['price']
            })

    df = pd.DataFrame(rows)
    restaurants_before_filter = df['restaurant'].nunique() if len(df) > 0 else 0
    
    # Filter out zero prices
    df = df[df['price'] > 0]
    restaurants_after_filter = df['restaurant'].nunique() if len(df) > 0 else 0
    
    # Calculate metadata
    metadata = {
        'total_in_file': total_restaurants,
        'with_items': restaurants_before_filter,
        'with_valid_prices': restaurants_after_filter,
        'filtered_out': total_restaurants - restaurants_after_filter
    }
    
    return df, metadata

# Initialize Claude client
@st.cache_resource
def get_claude_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    return None

def get_ai_recommendations(item_name, your_price, ingredient_cost, competitor_data, category):
    """Generate AI recommendations using Claude"""
    client = get_claude_client()

    if not client:
        return None

    # Prepare context
    profit_margin = ((your_price - ingredient_cost) / your_price) * 100
    avg_competitor = competitor_data['price'].mean()

    prompt = f"""You're a restaurant pricing consultant. Analyze this menu item and provide specific, actionable pricing recommendations.

ITEM DETAILS:
- Item: {item_name}
- Current Price: €{your_price:.2f}
- Ingredient Cost: €{ingredient_cost:.2f}
- Profit Margin: {profit_margin:.1f}%
- Category: {category}

COMPETITOR DATA:
- Number of competitors: {len(competitor_data)}
- Average competitor price: €{avg_competitor:.2f}
- Price range: €{competitor_data['price'].min():.2f} - €{competitor_data['price'].max():.2f}

Provide:
1. A clear recommendation (increase, decrease, or maintain price)
2. Specific suggested price with reasoning
3. Expected profit impact
4. One strategic insight

Keep it concise and practical. Format as bullet points."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

# Header
st.markdown('<p class="main-header">💰 Menu Price Optimizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Data-driven pricing for cafes and restaurants in Maastricht</p>', unsafe_allow_html=True)

# Load data
try:
    df, metadata = load_data()

    # Better navigation with tabs instead of sidebar radio
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview",
        "🔍 Competitor Analysis",
        "💵 Profit Calculator",
        "🤖 AI Recommendations",
        "🔄 Data Collection"
    ])

    with tab1:
        st.markdown("### 📊 Market Overview - Maastricht Restaurants")
        st.markdown("Complete view of **ALL** restaurants on Thuisbezorgd in Maastricht region. Get comprehensive competitive intelligence from the entire market.")

        # Show data scope info
        st.success(f"✅ **Data Scope:** Showing all {metadata['with_valid_prices']} restaurants from Thuisbezorgd Maastricht with complete menu pricing data.")

        # Show data quality info if restaurants were filtered out
        if metadata['filtered_out'] > 0:
            st.info(f"ℹ️ **Data Quality Note:** {metadata['filtered_out']} additional restaurants were found but filtered out due to incomplete data (no menu items or missing prices). "
                   f"Total restaurants discovered: {metadata['total_in_file']}. Use the Data Collection tab to re-scrape for the most current data.")

        with st.expander("ℹ️ How to use this tab"):
            st.markdown("""
            **What you'll find here:**
            - 📊 **Key Metrics**: Overview of ALL restaurants, items, and price ranges in Maastricht
            - 🏷️ **Category Grid**: Visual overview of all menu categories with average prices
            - 📈 **Charts**: Price distribution, restaurant comparisons, and market insights
            - 🔍 **Filters**: Narrow down by restaurant type and price range

            **Data Collection:**
            - Use the **🔄 Data Collection** tab to scrape all restaurants from Thuisbezorgd
            - No command line needed - everything works in-app!
            - Choose to scrape ALL restaurants (recommended) or set a custom limit

            **Tips:**
            - Click on category cards to see which categories have the highest prices
            - Use filters to focus on specific restaurant types or price ranges
            - Check the price distribution to see where your items fit in the market
            - Refresh data regularly using the Data Collection tab to stay current
            """)

        st.markdown("---")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🏪 Restaurants", df['restaurant'].nunique())
        with col2:
            st.metric("📋 Menu Items", len(df))
        with col3:
            st.metric("💰 Avg Price", f"€{df['price'].mean():.2f}")
        with col4:
            st.metric("📊 Price Range", f"€{df['price'].min():.2f} - €{df['price'].max():.2f}")

        st.markdown("---")

        # Category Overview - Show all categories at a glance
        st.markdown("#### 🏷️ Categories Overview")
        st.markdown("Quick view of all menu categories and their average prices")

        category_stats_for_grid = df.groupby('category').agg({
            'price': ['mean', 'count']
        }).round(2)
        category_stats_for_grid.columns = ['avg_price', 'count']
        category_stats_for_grid = category_stats_for_grid.reset_index().sort_values('avg_price', ascending=False)

        # Display categories in a grid layout
        cols_per_row = 4
        categories_list = category_stats_for_grid.to_dict('records')

        for i in range(0, len(categories_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(categories_list):
                    cat = categories_list[i + j]
                    with col:
                        st.markdown(f"""
                        <div class="category-card">
                            <div class="category-name">{cat['category']}</div>
                            <div class="category-stats">{int(cat['count'])} items</div>
                            <div class="category-price">€{cat['avg_price']:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")

        # Restaurant type and price range filters with better UX
        st.markdown("### 🔍 Filter Market Data")
        st.markdown("Filter the competitive landscape to focus on your restaurant type and price segment")

        col1, col2, col3 = st.columns(3)
        with col1:
            # Restaurant types filter
            all_types = set()
            for types_str in df['restaurant_types'].unique():
                all_types.update([t.strip() for t in types_str.split(',')])
            all_types = sorted(list(all_types))

            selected_type = st.selectbox(
                "🍽️ Restaurant Type",
                ['All Types'] + all_types,
                key="overview_type_filter",
                help="Filter to see only specific restaurant types (e.g., Asian, Pizza, Burgers)"
            )

        with col2:
            # Price range filter
            price_ranges = ['All'] + sorted(df['price_range'].unique().tolist())
            selected_price_range = st.selectbox(
                "💰 Price Range",
                price_ranges,
                key="overview_price_filter",
                help="Filter by price segment (budget, moderate, premium, luxury)"
            )

        with col3:
            # Show filtering stats
            if selected_type != 'All Types' or selected_price_range != 'All':
                st.markdown("#### Active Filters")
                if selected_type != 'All Types':
                    st.success(f"✓ {selected_type}")
                if selected_price_range != 'All':
                    st.success(f"✓ {selected_price_range}")

        # Apply filters
        filtered_overview_df = df.copy()
        if selected_type != 'All Types':
            filtered_overview_df = filtered_overview_df[
                filtered_overview_df['restaurant_types'].str.contains(selected_type, case=False, na=False)
            ]
        if selected_price_range != 'All':
            filtered_overview_df = filtered_overview_df[
                filtered_overview_df['price_range'] == selected_price_range
            ]

        if len(filtered_overview_df) == 0:
            st.warning(f"⚠️ No restaurants match your filters ({selected_type}, {selected_price_range}). Showing all data instead.")
            filtered_overview_df = df  # Fallback to show all data
        else:
            # Show filtered stats
            filtered_restaurants = filtered_overview_df['restaurant'].nunique()
            total_restaurants = df['restaurant'].nunique()
            if selected_type != 'All Types' or selected_price_range != 'All':
                st.info(f"📊 Showing **{filtered_restaurants}** of **{total_restaurants}** restaurants matching your filters")

        # Show restaurant type breakdown
        st.markdown("---")
        st.markdown("### 📊 Restaurant Type Breakdown")
        st.markdown("See the competitive landscape by restaurant type in your market")

        # Calculate restaurant type stats
        type_breakdown = []
        for types_str in df['restaurant_types'].unique():
            for rtype in types_str.split(','):
                rtype = rtype.strip()
                type_df = df[df['restaurant_types'].str.contains(rtype, case=False, na=False)]
                type_restaurants = type_df['restaurant'].nunique()
                type_items = len(type_df)
                type_avg_price = type_df['price'].mean()
                type_breakdown.append({
                    'Type': rtype.title(),
                    'Restaurants': type_restaurants,
                    'Menu Items': type_items,
                    'Avg Price': type_avg_price
                })

        # Remove duplicates and sort
        type_breakdown_df = pd.DataFrame(type_breakdown).drop_duplicates('Type').sort_values('Restaurants', ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Bar chart of restaurant types
            fig = px.bar(
                type_breakdown_df,
                x='Type',
                y='Restaurants',
                title='Number of Restaurants by Type in Maastricht',
                labels={'Restaurants': 'Number of Restaurants', 'Type': 'Restaurant Type'},
                color='Avg Price',
                color_continuous_scale='RdYlGn_r',
                text='Restaurants'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=True, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🎯 Your Competitive Set")
            st.markdown("Filter by your restaurant type to see:")
            st.markdown("- **Number of competitors**")
            st.markdown("- **Average pricing**")
            st.markdown("- **Popular menu items**")
            st.markdown("- **Price positioning**")

            st.markdown("---")
            st.markdown("**Example: Asian Restaurants**")
            asian_df = df[df['restaurant_types'].str.contains('asian', case=False, na=False)]
            if len(asian_df) > 0:
                asian_restaurants = asian_df['restaurant'].nunique()
                asian_avg = asian_df['price'].mean()
                st.metric("Asian Restaurants", asian_restaurants)
                st.metric("Avg Price", f"€{asian_avg:.2f}")
            else:
                st.info("Select restaurant type to see competitive insights")

        # Show all restaurants table
        st.markdown("---")
        st.markdown("### 🏪 All Restaurants in Dataset")
        st.markdown("Complete list of restaurants with pricing data")

        # Create restaurant summary
        restaurant_summary = df.groupby('restaurant').agg({
            'item_name': 'count',
            'price': ['mean', 'min', 'max'],
            'restaurant_types': 'first',
            'price_range': 'first'
        }).reset_index()

        restaurant_summary.columns = ['Restaurant', 'Menu Items', 'Avg Price', 'Min Price', 'Max Price', 'Types', 'Price Range']
        restaurant_summary = restaurant_summary.sort_values('Restaurant')

        # Format pricing columns
        restaurant_summary['Avg Price'] = restaurant_summary['Avg Price'].apply(lambda x: f"€{x:.2f}")
        restaurant_summary['Min Price'] = restaurant_summary['Min Price'].apply(lambda x: f"€{x:.2f}")
        restaurant_summary['Max Price'] = restaurant_summary['Max Price'].apply(lambda x: f"€{x:.2f}")

        # Display table
        st.dataframe(
            restaurant_summary,
            use_container_width=True,
            hide_index=True,
            height=min(len(restaurant_summary) * 40 + 50, 400)  # Dynamic height, max 400px
        )

        # Data quality insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Total Restaurants", len(restaurant_summary))
        with col2:
            total_items = df['item_name'].count()
            st.metric("📋 Total Menu Items", total_items)
        with col3:
            avg_items_per_restaurant = total_items / len(restaurant_summary)
            st.metric("📊 Avg Items/Restaurant", f"{avg_items_per_restaurant:.0f}")

        st.markdown("---")

        # Price distribution
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Price Distribution")
            fig = px.histogram(filtered_overview_df, x='price', nbins=15,
                             labels={'price': 'Price (€)', 'count': 'Number of Items'},
                             color_discrete_sequence=['#667eea'])
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Average Price by Restaurant")
            restaurant_avg = filtered_overview_df.groupby('restaurant')['price'].mean().sort_values(ascending=False)
            fig = px.bar(x=restaurant_avg.values, y=restaurant_avg.index,
                        orientation='h',
                        labels={'x': 'Average Price (€)', 'y': ''},
                        color=restaurant_avg.values,
                        color_continuous_scale='Viridis')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Restaurant Type Distribution
        st.markdown("#### Restaurant Type Distribution")
        col1, col2 = st.columns(2)

        with col1:
            # Count by type
            type_counts = {}
            for types_str in df['restaurant_types'].unique():
                for t in types_str.split(','):
                    t = t.strip()
                    type_counts[t] = type_counts.get(t, 0) + 1

            type_df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Count'])
            type_df = type_df.sort_values('Count', ascending=False)

            fig = px.bar(type_df, x='Type', y='Count',
                        labels={'Type': 'Restaurant Type', 'Count': 'Number of Restaurants'},
                        color='Count',
                        color_continuous_scale='Teal')
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Price range distribution
            price_range_counts = df.groupby('price_range')['restaurant'].nunique()
            fig = px.pie(values=price_range_counts.values, names=price_range_counts.index,
                        title='Restaurants by Price Range',
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Category breakdown
        st.markdown("#### Prices by Category")
        category_stats = filtered_overview_df.groupby('category').agg({
            'price': ['mean', 'min', 'max', 'count']
        }).round(2)
        category_stats.columns = ['Avg Price (€)', 'Min Price (€)', 'Max Price (€)', 'Items']
        category_stats = category_stats.sort_values('Avg Price (€)', ascending=False)
        st.dataframe(category_stats, use_container_width=True)

    with tab2:
        st.markdown("### 🔍 Competitor Analysis")
        st.markdown("Analyze competitor pricing by category. Select one or more categories to compare.")

        with st.expander("ℹ️ How to use this tab"):
            st.markdown("""
            **What you'll find here:**
            - 🏷️ **Category Selection**: Choose multiple categories to compare
            - 📊 **Statistics**: Key metrics for selected categories
            - 📋 **Detailed Table**: All items with prices sorted high to low
            - 📦 **Box Plots**: Visual comparison of price ranges by restaurant

            **Tips:**
            - Select multiple categories to compare pricing across different item types
            - Check the detailed table to see specific competitor items and prices
            - Use box plots to identify price outliers and positioning opportunities
            """)

        st.markdown("---")

        # Multi-select for categories
        all_categories = sorted(df['category'].unique().tolist())
        selected_categories = st.multiselect(
            "🏷️ Select Categories to Analyze",
            all_categories,
            default=[all_categories[0]] if all_categories else [],
            key="comp_category",
            help="Choose one or more categories to see detailed pricing analysis"
        )

        if selected_categories:
            filtered_df = df[df['category'].isin(selected_categories)]
        else:
            filtered_df = df
            st.info("💡 Select at least one category to view specific analysis, or leave empty to see all items.")

        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Items", len(filtered_df))
        with col2:
            st.metric("💰 Average Price", f"€{filtered_df['price'].mean():.2f}")
        with col3:
            st.metric("📊 Price Range", f"€{filtered_df['price'].min():.2f} - €{filtered_df['price'].max():.2f}")

        st.markdown("---")

        # Detailed table
        st.markdown("#### All Items in Category")
        display_df = filtered_df[['restaurant', 'item_name', 'category', 'price']].sort_values('price', ascending=False)
        display_df['price'] = display_df['price'].apply(lambda x: f"€{x:.2f}")
        st.dataframe(display_df, use_container_width=True, height=400)

        # Price positioning
        st.markdown("#### Price Distribution by Restaurant")
        fig = px.box(filtered_df, x='restaurant', y='price',
                    labels={'price': 'Price (€)', 'restaurant': ''},
                    color='restaurant')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### 💵 Professional Profit Calculator")
        st.markdown("Complete suite of financial tools for restaurant owners - from recipe costing to menu engineering.")

        with st.expander("ℹ️ Guide to Restaurant Profit Calculations"):
            st.markdown("""
            **Essential Metrics for Restaurant Success:**

            1. **Recipe Builder** 🧾
               - Calculate exact ingredient costs
               - Track multiple ingredients with units and quantities
               - Get accurate portion costs for each menu item

            2. **Food Cost Percentage** 📊
               - Industry standard: 28-35% for restaurants
               - Lower is better (more profit margin)
               - Formula: (Ingredient Cost / Selling Price) × 100

            3. **Menu Engineering** 🎯
               - Analyze profitability vs. popularity
               - Identify stars (high profit, high sales), plow horses, puzzles, and dogs
               - Optimize your menu mix

            4. **Break-Even Analysis** ⚖️
               - Calculate how many units to sell to cover fixed costs
               - Understand your minimum sales targets
               - Plan for profitability

            5. **Prime Cost** 💼
               - Food Cost + Labor Cost
               - Should be under 60% of revenue
               - Key metric for restaurant health

            6. **Target Pricing** 🎯
               - Work backwards from desired profit margin
               - See competitive positioning
               - Find optimal price points

            **Industry Benchmarks:**
            - Food Cost: 28-35%
            - Labor Cost: 25-35%
            - Prime Cost: <60%
            - Net Profit Margin: 10-15%
            """)

        # Create calculator mode selector
        calc_mode = st.radio(
            "Select Calculator:",
            ["🧾 Recipe Builder", "📊 Quick Profit Calculator", "🎯 Menu Engineering", "⚖️ Break-Even Analysis", "💼 Prime Cost Calculator", "🎯 Target Pricing"],
            horizontal=True,
            key="calc_mode"
        )

        st.markdown("---")

        # RECIPE BUILDER
        if calc_mode == "🧾 Recipe Builder":
            st.markdown("### 🧾 Recipe Builder & Cost Calculator")
            st.markdown("Build your recipe with precise ingredient quantities and costs. Perfect for accurate portion costing.")

            col1, col2 = st.columns([2, 1])

            with col1:
                item_name = st.text_input(
                    "Recipe Name",
                    "Classic Burger",
                    key="recipe_name",
                    help="Name of your menu item"
                )

                servings = st.number_input(
                    "Number of Servings",
                    min_value=1,
                    value=1,
                    step=1,
                    key="recipe_servings",
                    help="How many servings does this recipe make?"
                )

            with col2:
                st.markdown("#### 💡 Quick Tips")
                st.info("""
                - Enter all ingredients used
                - Be precise with quantities
                - Include packaging/garnish
                - Update costs regularly
                """)

            st.markdown("---")
            st.markdown("### 📝 Ingredients")

            # Initialize session state for ingredients
            if 'ingredients' not in st.session_state:
                st.session_state.ingredients = [
                    {"name": "Burger Patty (150g)", "quantity": 1.0, "unit": "piece", "cost_per_unit": 1.50},
                    {"name": "Bun", "quantity": 1.0, "unit": "piece", "cost_per_unit": 0.40},
                    {"name": "Lettuce", "quantity": 30.0, "unit": "g", "cost_per_unit": 0.01},
                    {"name": "Tomato", "quantity": 50.0, "unit": "g", "cost_per_unit": 0.008},
                    {"name": "Cheese Slice", "quantity": 1.0, "unit": "piece", "cost_per_unit": 0.30},
                ]

            # Display ingredients table
            for idx, ingredient in enumerate(st.session_state.ingredients):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1.5, 1, 1.5, 1.5, 0.5])

                with col1:
                    ingredient['name'] = st.text_input(
                        "Ingredient",
                        ingredient['name'],
                        key=f"ing_name_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col2:
                    ingredient['quantity'] = st.number_input(
                        "Quantity",
                        min_value=0.0,
                        value=ingredient['quantity'],
                        step=0.1,
                        key=f"ing_qty_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col3:
                    ingredient['unit'] = st.selectbox(
                        "Unit",
                        ["g", "kg", "ml", "L", "piece", "oz", "lb"],
                        index=["g", "kg", "ml", "L", "piece", "oz", "lb"].index(ingredient['unit']),
                        key=f"ing_unit_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col4:
                    ingredient['cost_per_unit'] = st.number_input(
                        "Cost/Unit (€)",
                        min_value=0.0,
                        value=ingredient['cost_per_unit'],
                        step=0.01,
                        format="%.3f",
                        key=f"ing_cost_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col5:
                    total_cost = ingredient['quantity'] * ingredient['cost_per_unit']
                    st.metric(
                        "Total",
                        f"€{total_cost:.2f}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col6:
                    if st.button("❌", key=f"remove_{idx}", help="Remove ingredient"):
                        st.session_state.ingredients.pop(idx)
                        st.rerun()

            # Add ingredient button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("➕ Add Ingredient", type="secondary"):
                    st.session_state.ingredients.append({
                        "name": "New Ingredient",
                        "quantity": 1.0,
                        "unit": "piece",
                        "cost_per_unit": 0.50
                    })
                    st.rerun()

            # Calculate total recipe cost
            total_recipe_cost = sum(ing['quantity'] * ing['cost_per_unit'] for ing in st.session_state.ingredients)
            cost_per_serving = total_recipe_cost / servings

            st.markdown("---")
            st.markdown("### 💰 Recipe Cost Analysis")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Recipe Cost", f"€{total_recipe_cost:.2f}")
            with col2:
                st.metric("Cost Per Serving", f"€{cost_per_serving:.2f}")
            with col3:
                st.metric("Number of Servings", servings)

            st.markdown("---")
            st.markdown("### 💵 Pricing & Profitability")

            col1, col2 = st.columns(2)

            with col1:
                selling_price = st.number_input(
                    "Selling Price per Serving (€)",
                    min_value=0.0,
                    value=round(cost_per_serving * 3.2, 2),  # Default 30% food cost
                    step=0.10,
                    key="recipe_price"
                )

                labor_cost_per_serving = st.number_input(
                    "Labor Cost per Serving (€)",
                    min_value=0.0,
                    value=round(cost_per_serving * 0.5, 2),
                    step=0.10,
                    key="recipe_labor",
                    help="Time to prepare × hourly wage / number of servings"
                )

            if selling_price > 0:
                profit_per_serving = selling_price - cost_per_serving - labor_cost_per_serving
                food_cost_pct = (cost_per_serving / selling_price) * 100
                labor_cost_pct = (labor_cost_per_serving / selling_price) * 100
                prime_cost_pct = food_cost_pct + labor_cost_pct
                profit_margin_pct = (profit_per_serving / selling_price) * 100

                with col2:
                    st.markdown("#### 📊 Key Metrics")

                    # Food cost percentage with color coding
                    if food_cost_pct <= 30:
                        st.success(f"**Food Cost:** {food_cost_pct:.1f}% ✓ Excellent")
                    elif food_cost_pct <= 35:
                        st.info(f"**Food Cost:** {food_cost_pct:.1f}% → Good")
                    else:
                        st.warning(f"**Food Cost:** {food_cost_pct:.1f}% ⚠ High")

                    # Prime cost
                    if prime_cost_pct <= 60:
                        st.success(f"**Prime Cost:** {prime_cost_pct:.1f}% ✓")
                    else:
                        st.warning(f"**Prime Cost:** {prime_cost_pct:.1f}% ⚠")

                    st.metric("Profit Margin", f"{profit_margin_pct:.1f}%")

                st.markdown("---")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Food Cost", f"€{cost_per_serving:.2f}", f"{food_cost_pct:.1f}%")
                with col2:
                    st.metric("Labor Cost", f"€{labor_cost_per_serving:.2f}", f"{labor_cost_pct:.1f}%")
                with col3:
                    st.metric("Profit/Item", f"€{profit_per_serving:.2f}", f"{profit_margin_pct:.1f}%")
                with col4:
                    st.metric("Selling Price", f"€{selling_price:.2f}")

                # Monthly projections
                st.markdown("---")
                st.markdown("### 📈 Monthly Projections")

                monthly_sales = st.slider(
                    "Estimated Monthly Sales",
                    10, 1000, 200, 10,
                    key="recipe_monthly_sales",
                    help="How many units do you expect to sell per month?"
                )

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Monthly Revenue", f"€{selling_price * monthly_sales:.2f}")
                with col2:
                    st.metric("Monthly Food Cost", f"€{cost_per_serving * monthly_sales:.2f}")
                with col3:
                    st.metric("Monthly Labor Cost", f"€{labor_cost_per_serving * monthly_sales:.2f}")
                with col4:
                    st.metric("Monthly Profit", f"€{profit_per_serving * monthly_sales:.2f}")

        # QUICK PROFIT CALCULATOR
        elif calc_mode == "📊 Quick Profit Calculator":
            st.markdown("### 📊 Quick Profit Calculator")
            st.markdown("Fast calculation for single items with market comparison.")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("#### 📝 Your Menu Item")
                item_name = st.text_input(
                    "Item Name",
                    "Cappuccino",
                    key="quick_item",
                    help="Enter the name of your menu item"
                )
                your_price = st.number_input(
                    "Your Selling Price (€)",
                    min_value=0.0,
                    value=3.50,
                    step=0.10,
                    key="quick_price",
                    help="The price you charge customers"
                )
                ingredient_cost = st.number_input(
                    "Ingredient Cost (€)",
                    min_value=0.0,
                    value=0.80,
                    step=0.10,
                    key="quick_cost",
                    help="Total cost of ingredients per item"
                )

            with col2:
                st.markdown("#### 🔍 Compare with Category")
                compare_category = st.selectbox(
                    "Category",
                    sorted(df['category'].unique()),
                    key="quick_category",
                    help="Select a category to compare against competitor pricing"
                )

                competitor_items = df[df['category'] == compare_category]
                if len(competitor_items) > 0:
                    avg_competitor_price = competitor_items['price'].mean()
                    min_competitor_price = competitor_items['price'].min()
                    max_competitor_price = competitor_items['price'].max()

                    st.metric("Competitor Average", f"€{avg_competitor_price:.2f}")
                    st.metric("Competitor Range", f"€{min_competitor_price:.2f} - €{max_competitor_price:.2f}")

            # Calculate margins
            if your_price > 0:
                profit_per_item = your_price - ingredient_cost
                margin_percentage = (profit_per_item / your_price) * 100
                food_cost_pct = (ingredient_cost / your_price) * 100

                # Display results
                st.markdown("---")
                st.markdown("### 💰 Your Profit Analysis")

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("Profit per Item", f"€{profit_per_item:.2f}")
                with col2:
                    if food_cost_pct <= 30:
                        st.metric("Food Cost %", f"{food_cost_pct:.1f}%", delta="✓ Excellent", delta_color="normal")
                    elif food_cost_pct <= 35:
                        st.metric("Food Cost %", f"{food_cost_pct:.1f}%", delta="Good", delta_color="normal")
                    else:
                        st.metric("Food Cost %", f"{food_cost_pct:.1f}%", delta="⚠ High", delta_color="inverse")
                with col3:
                    st.metric("Profit Margin", f"{margin_percentage:.1f}%")
                with col4:
                    st.metric("Competitor Avg", f"€{avg_competitor_price:.2f}")
                with col5:
                    price_diff = your_price - avg_competitor_price
                    st.metric("Price vs Market", f"€{price_diff:.2f}",
                             delta=f"{((price_diff/avg_competitor_price)*100):.1f}%")

                # Recommendations
                st.markdown("---")
                st.markdown("### 📊 Pricing Recommendations")

                if your_price < avg_competitor_price * 0.9:
                    st.success(f"✅ **You're priced competitively!** Your price is {((avg_competitor_price - your_price) / avg_competitor_price * 100):.1f}% below average.")
                    potential_increase = avg_competitor_price - your_price
                    st.info(f"💡 **Opportunity:** You could increase to €{avg_competitor_price:.2f} (competitor average) and add €{potential_increase:.2f} profit per sale.")
                elif your_price > avg_competitor_price * 1.1:
                    st.warning(f"⚠️ **You're priced above market** ({((your_price - avg_competitor_price) / avg_competitor_price * 100):.1f}% higher). Consider adjusting to €{avg_competitor_price:.2f} (competitor average).")
                else:
                    st.success(f"✅ **Perfect positioning!** You're right in the competitive range (within 10% of market average).")

                # What-if analysis
                st.markdown("---")
                st.markdown("### 🔮 What-If Analysis")

                monthly_sales = st.slider("Estimated monthly sales", 50, 1000, 200, 10, key="quick_sales")

                # Calculate scenarios
                scenarios_data = []

                # Current scenario
                scenarios_data.append({
                    'Scenario': '📍 Current Price',
                    'Price (€)': your_price,
                    'Profit/Item (€)': profit_per_item,
                    'Monthly Profit (€)': profit_per_item * monthly_sales,
                    'Food Cost %': food_cost_pct,
                    'vs Competitor': 'Your current pricing'
                })

                # Match competitor average
                if avg_competitor_price > 0:
                    new_profit = avg_competitor_price - ingredient_cost
                    diff = (new_profit * monthly_sales) - (profit_per_item * monthly_sales)
                    new_food_cost = (ingredient_cost / avg_competitor_price) * 100
                    scenarios_data.append({
                        'Scenario': '🎯 Match Market Avg',
                        'Price (€)': avg_competitor_price,
                        'Profit/Item (€)': new_profit,
                        'Monthly Profit (€)': new_profit * monthly_sales,
                        'Food Cost %': new_food_cost,
                        'vs Competitor': f"+€{diff:.2f}/month" if diff > 0 else f"€{diff:.2f}/month"
                    })

                # Optimal food cost (30%)
                optimal_price = ingredient_cost / 0.30
                optimal_profit = optimal_price - ingredient_cost
                optimal_diff = (optimal_profit * monthly_sales) - (profit_per_item * monthly_sales)
                scenarios_data.append({
                    'Scenario': '🎯 30% Food Cost',
                    'Price (€)': optimal_price,
                    'Profit/Item (€)': optimal_profit,
                    'Monthly Profit (€)': optimal_profit * monthly_sales,
                    'Food Cost %': 30.0,
                    'vs Competitor': f"+€{optimal_diff:.2f}/month" if optimal_diff > 0 else f"€{optimal_diff:.2f}/month"
                })

                scenarios_df = pd.DataFrame(scenarios_data)
                scenarios_df['Price (€)'] = scenarios_df['Price (€)'].apply(lambda x: f"{x:.2f}")
                scenarios_df['Profit/Item (€)'] = scenarios_df['Profit/Item (€)'].apply(lambda x: f"{x:.2f}")
                scenarios_df['Monthly Profit (€)'] = scenarios_df['Monthly Profit (€)'].apply(lambda x: f"{x:.2f}")
                scenarios_df['Food Cost %'] = scenarios_df['Food Cost %'].apply(lambda x: f"{x:.1f}%")

                st.dataframe(scenarios_df, use_container_width=True, hide_index=True)

        # MENU ENGINEERING
        elif calc_mode == "🎯 Menu Engineering":
            st.markdown("### 🎯 Menu Engineering Matrix")
            st.markdown("Analyze your menu items by profitability and popularity. Identify your Stars, Plow Horses, Puzzles, and Dogs.")

            with st.expander("📚 Understanding Menu Engineering"):
                st.markdown("""
                **The Four Categories:**

                1. **⭐ STARS** (High Profit, High Popularity)
                   - Your best performers!
                   - Feature prominently on menu
                   - Maintain quality and consistency
                   - Consider slight price increases

                2. **🐴 PLOW HORSES** (Low Profit, High Popularity)
                   - Popular but not profitable
                   - Try to increase price slightly
                   - Reduce portion size
                   - Lower ingredient costs

                3. **🧩 PUZZLES** (High Profit, Low Popularity)
                   - Profitable but not selling well
                   - Improve menu description
                   - Reposition on menu
                   - Train staff to upsell
                   - Consider renaming

                4. **🐕 DOGS** (Low Profit, Low Popularity)
                   - Consider removing from menu
                   - Taking up valuable menu space
                   - May confuse customers
                   - Replace with potential stars
                """)

            st.markdown("#### 📝 Enter Your Menu Items")
            st.markdown("Add at least 4-5 items for meaningful analysis")

            # Initialize session state for menu items
            if 'menu_items' not in st.session_state:
                st.session_state.menu_items = [
                    {"name": "Classic Burger", "price": 12.50, "cost": 3.80, "monthly_sales": 180},
                    {"name": "Margherita Pizza", "price": 9.50, "cost": 2.50, "monthly_sales": 240},
                    {"name": "Caesar Salad", "price": 8.50, "cost": 3.20, "monthly_sales": 95},
                    {"name": "Truffle Pasta", "price": 16.50, "cost": 4.50, "monthly_sales": 65},
                    {"name": "House Sandwich", "price": 7.50, "cost": 2.80, "monthly_sales": 145},
                ]

            # Display menu items table
            for idx, item in enumerate(st.session_state.menu_items):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1.5, 1.5, 1.5, 1.5, 0.5])

                with col1:
                    item['name'] = st.text_input(
                        "Item Name",
                        item['name'],
                        key=f"menu_name_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col2:
                    item['price'] = st.number_input(
                        "Price (€)",
                        min_value=0.0,
                        value=item['price'],
                        step=0.10,
                        key=f"menu_price_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col3:
                    item['cost'] = st.number_input(
                        "Cost (€)",
                        min_value=0.0,
                        value=item['cost'],
                        step=0.10,
                        key=f"menu_cost_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col4:
                    item['monthly_sales'] = st.number_input(
                        "Monthly Sales",
                        min_value=0,
                        value=item['monthly_sales'],
                        step=10,
                        key=f"menu_sales_{idx}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col5:
                    profit = item['price'] - item['cost']
                    st.metric(
                        "Profit",
                        f"€{profit:.2f}",
                        label_visibility="collapsed" if idx > 0 else "visible"
                    )
                with col6:
                    if st.button("❌", key=f"menu_remove_{idx}", help="Remove item"):
                        st.session_state.menu_items.pop(idx)
                        st.rerun()

            # Add item button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("➕ Add Menu Item", type="secondary"):
                    st.session_state.menu_items.append({
                        "name": "New Item",
                        "price": 10.0,
                        "cost": 3.0,
                        "monthly_sales": 100
                    })
                    st.rerun()

            if len(st.session_state.menu_items) >= 3:
                st.markdown("---")
                st.markdown("### 📊 Menu Engineering Analysis")

                # Calculate metrics for each item
                menu_df = pd.DataFrame(st.session_state.menu_items)
                menu_df['profit_per_item'] = menu_df['price'] - menu_df['cost']
                menu_df['total_profit'] = menu_df['profit_per_item'] * menu_df['monthly_sales']
                menu_df['food_cost_pct'] = (menu_df['cost'] / menu_df['price']) * 100

                # Calculate averages
                avg_profit = menu_df['profit_per_item'].mean()
                avg_sales = menu_df['monthly_sales'].mean()

                # Classify items
                def classify_item(row):
                    high_profit = row['profit_per_item'] >= avg_profit
                    high_sales = row['monthly_sales'] >= avg_sales

                    if high_profit and high_sales:
                        return "⭐ Star"
                    elif high_profit and not high_sales:
                        return "🧩 Puzzle"
                    elif not high_profit and high_sales:
                        return "🐴 Plow Horse"
                    else:
                        return "🐕 Dog"

                menu_df['category'] = menu_df.apply(classify_item, axis=1)

                # Display summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    stars = len(menu_df[menu_df['category'] == "⭐ Star"])
                    st.metric("⭐ Stars", stars)
                with col2:
                    puzzles = len(menu_df[menu_df['category'] == "🧩 Puzzle"])
                    st.metric("🧩 Puzzles", puzzles)
                with col3:
                    plow_horses = len(menu_df[menu_df['category'] == "🐴 Plow Horse"])
                    st.metric("🐴 Plow Horses", plow_horses)
                with col4:
                    dogs = len(menu_df[menu_df['category'] == "🐕 Dog"])
                    st.metric("🐕 Dogs", dogs)

                # Display classified items
                st.markdown("---")
                display_df = menu_df[['name', 'price', 'profit_per_item', 'monthly_sales', 'total_profit', 'food_cost_pct', 'category']].copy()
                display_df.columns = ['Item', 'Price (€)', 'Profit/Item (€)', 'Monthly Sales', 'Monthly Profit (€)', 'Food Cost %', 'Classification']
                display_df['Price (€)'] = display_df['Price (€)'].apply(lambda x: f"€{x:.2f}")
                display_df['Profit/Item (€)'] = display_df['Profit/Item (€)'].apply(lambda x: f"€{x:.2f}")
                display_df['Monthly Profit (€)'] = display_df['Monthly Profit (€)'].apply(lambda x: f"€{x:.2f}")
                display_df['Food Cost %'] = display_df['Food Cost %'].apply(lambda x: f"{x:.1f}%")

                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Scatter plot
                st.markdown("---")
                st.markdown("### 📈 Visual Menu Engineering Matrix")

                fig = px.scatter(
                    menu_df,
                    x='monthly_sales',
                    y='profit_per_item',
                    size='total_profit',
                    color='category',
                    text='name',
                    title='Menu Engineering Matrix',
                    labels={
                        'monthly_sales': 'Monthly Sales (Popularity) →',
                        'profit_per_item': 'Profit per Item (€) →'
                    },
                    color_discrete_map={
                        "⭐ Star": "#FFD700",
                        "🧩 Puzzle": "#9370DB",
                        "🐴 Plow Horse": "#CD853F",
                        "🐕 Dog": "#808080"
                    }
                )

                # Add average lines
                fig.add_hline(y=avg_profit, line_dash="dash", line_color="gray", annotation_text="Avg Profit")
                fig.add_vline(x=avg_sales, line_dash="dash", line_color="gray", annotation_text="Avg Sales")

                fig.update_traces(textposition='top center')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                # Recommendations
                st.markdown("---")
                st.markdown("### 💡 Recommendations")

                for _, row in menu_df.iterrows():
                    if row['category'] == "⭐ Star":
                        st.success(f"**{row['name']}** - Keep doing what you're doing! Consider featuring more prominently.")
                    elif row['category'] == "🧩 Puzzle":
                        st.info(f"**{row['name']}** - Profitable but low sales. Improve menu placement or description. Train staff to recommend it.")
                    elif row['category'] == "🐴 Plow Horse":
                        st.warning(f"**{row['name']}** - Popular but low profit margin ({row['food_cost_pct']:.1f}% food cost). Try small price increase or reduce costs.")
                    elif row['category'] == "🐕 Dog":
                        st.error(f"**{row['name']}** - Consider removing from menu. Low profit and low popularity.")

        # BREAK-EVEN ANALYSIS
        elif calc_mode == "⚖️ Break-Even Analysis":
            st.markdown("### ⚖️ Break-Even Analysis")
            st.markdown("Calculate how many units you need to sell to cover your fixed costs and start making profit.")

            with st.expander("💡 Understanding Break-Even"):
                st.markdown("""
                **Break-Even Point** = Fixed Costs ÷ (Selling Price - Variable Cost per Unit)

                **Fixed Costs:** Expenses that don't change with sales volume
                - Rent, insurance, salaries, utilities, etc.

                **Variable Costs:** Expenses that change with each unit sold
                - Ingredients, packaging, delivery fees

                **Contribution Margin:** Selling Price - Variable Cost
                - The amount each sale contributes to covering fixed costs
                """)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 💰 Fixed Costs (Monthly)")

                rent = st.number_input(
                    "Rent (€)",
                    min_value=0.0,
                    value=2500.0,
                    step=100.0,
                    key="be_rent"
                )
                salaries = st.number_input(
                    "Salaries (€)",
                    min_value=0.0,
                    value=6000.0,
                    step=100.0,
                    key="be_salaries"
                )
                utilities = st.number_input(
                    "Utilities (€)",
                    min_value=0.0,
                    value=500.0,
                    step=50.0,
                    key="be_utilities"
                )
                insurance = st.number_input(
                    "Insurance (€)",
                    min_value=0.0,
                    value=300.0,
                    step=50.0,
                    key="be_insurance"
                )
                other_fixed = st.number_input(
                    "Other Fixed Costs (€)",
                    min_value=0.0,
                    value=700.0,
                    step=50.0,
                    key="be_other"
                )

                total_fixed_costs = rent + salaries + utilities + insurance + other_fixed

                st.markdown("---")
                st.metric("**Total Fixed Costs**", f"€{total_fixed_costs:,.2f}", help="Monthly fixed costs")

            with col2:
                st.markdown("#### 📦 Per-Unit Information")

                selling_price_unit = st.number_input(
                    "Average Selling Price (€)",
                    min_value=0.0,
                    value=12.50,
                    step=0.50,
                    key="be_price",
                    help="Average price per menu item"
                )

                variable_cost_unit = st.number_input(
                    "Variable Cost per Unit (€)",
                    min_value=0.0,
                    value=4.50,
                    step=0.50,
                    key="be_variable",
                    help="Ingredient + packaging cost per item"
                )

                contribution_margin = selling_price_unit - variable_cost_unit

                if selling_price_unit > 0:
                    contribution_margin_pct = (contribution_margin / selling_price_unit) * 100
                else:
                    contribution_margin_pct = 0

                st.markdown("---")
                st.metric("**Contribution Margin**", f"€{contribution_margin:.2f}",
                         help="How much each sale contributes to fixed costs")
                st.metric("**Contribution Margin %**", f"{contribution_margin_pct:.1f}%")

            if contribution_margin > 0:
                st.markdown("---")
                st.markdown("### 📊 Break-Even Analysis Results")

                break_even_units = total_fixed_costs / contribution_margin
                break_even_revenue = break_even_units * selling_price_unit
                daily_break_even = break_even_units / 30  # Assuming 30 days/month

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Break-Even Units (Monthly)", f"{break_even_units:,.0f}",
                             help="Units needed to cover all fixed costs")
                with col2:
                    st.metric("Break-Even Revenue", f"€{break_even_revenue:,.2f}",
                             help="Revenue needed to break even")
                with col3:
                    st.metric("Daily Sales Needed", f"{daily_break_even:,.0f}",
                             help="Average units per day to break even")

                st.markdown("---")
                st.markdown("### 📈 Profit Scenarios")

                # Create profit scenarios
                scenarios = []
                for units in [int(break_even_units * 0.5), int(break_even_units * 0.75),
                             int(break_even_units), int(break_even_units * 1.25),
                             int(break_even_units * 1.5)]:
                    revenue = units * selling_price_unit
                    total_variable_costs = units * variable_cost_unit
                    profit = revenue - total_variable_costs - total_fixed_costs
                    profit_margin = (profit / revenue * 100) if revenue > 0 else 0

                    scenarios.append({
                        'Monthly Sales': units,
                        'Revenue (€)': revenue,
                        'Variable Costs (€)': total_variable_costs,
                        'Fixed Costs (€)': total_fixed_costs,
                        'Profit (€)': profit,
                        'Profit Margin %': profit_margin
                    })

                scenarios_df = pd.DataFrame(scenarios)
                scenarios_df['Monthly Sales'] = scenarios_df['Monthly Sales'].apply(lambda x: f"{x:,}")
                scenarios_df['Revenue (€)'] = scenarios_df['Revenue (€)'].apply(lambda x: f"€{x:,.2f}")
                scenarios_df['Variable Costs (€)'] = scenarios_df['Variable Costs (€)'].apply(lambda x: f"€{x:,.2f}")
                scenarios_df['Fixed Costs (€)'] = scenarios_df['Fixed Costs (€)'].apply(lambda x: f"€{x:,.2f}")
                scenarios_df['Profit (€)'] = scenarios_df['Profit (€)'].apply(lambda x: f"€{x:,.2f}")
                scenarios_df['Profit Margin %'] = scenarios_df['Profit Margin %'].apply(lambda x: f"{x:.1f}%")

                st.dataframe(scenarios_df, use_container_width=True, hide_index=True)

                # Visualization
                st.markdown("---")
                units_range = range(0, int(break_even_units * 2), max(1, int(break_even_units / 20)))
                revenues = [u * selling_price_unit for u in units_range]
                total_costs = [total_fixed_costs + (u * variable_cost_unit) for u in units_range]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(units_range), y=revenues, mode='lines', name='Revenue', line=dict(color='green')))
                fig.add_trace(go.Scatter(x=list(units_range), y=total_costs, mode='lines', name='Total Cost', line=dict(color='red')))
                fig.add_vline(x=break_even_units, line_dash="dash", line_color="blue", annotation_text="Break-Even Point")

                fig.update_layout(
                    title="Break-Even Chart",
                    xaxis_title="Units Sold",
                    yaxis_title="Amount (€)",
                    hovermode='x unified',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("⚠️ Contribution margin must be positive. Your selling price needs to be higher than variable costs.")

        # PRIME COST CALCULATOR
        elif calc_mode == "💼 Prime Cost Calculator":
            st.markdown("### 💼 Prime Cost Calculator")
            st.markdown("Calculate your Prime Cost (Food Cost + Labor Cost) - the most important metric for restaurant profitability.")

            with st.expander("💡 Understanding Prime Cost"):
                st.markdown("""
                **Prime Cost = Food Cost + Labor Cost**

                This is the single most important metric in restaurant management.

                **Industry Benchmarks:**
                - **Prime Cost should be < 60% of revenue**
                - Food Cost: 28-35%
                - Labor Cost: 25-35%
                - Total Prime Cost: 53-70% (target: <60%)

                **Why It Matters:**
                - If Prime Cost > 60%, you're leaving little room for other expenses and profit
                - These are your two largest controllable costs
                - Monitoring Prime Cost weekly helps catch problems early

                **How to Improve:**
                - Reduce food waste
                - Negotiate better supplier prices
                - Optimize staff scheduling
                - Cross-train employees
                - Review menu pricing regularly
                """)

            st.markdown("---")

            # Time period selector
            period = st.radio(
                "Calculate for:",
                ["Weekly", "Monthly", "Quarterly"],
                horizontal=True,
                key="prime_period"
            )

            period_multiplier = {"Weekly": 1, "Monthly": 4.33, "Quarterly": 13}[period]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🍽️ Food Costs")

                beginning_inventory = st.number_input(
                    f"Beginning Inventory (€)",
                    min_value=0.0,
                    value=3500.0,
                    step=100.0,
                    key="pc_begin_inv"
                )

                purchases = st.number_input(
                    f"Purchases (€)",
                    min_value=0.0,
                    value=8500.0 if period == "Monthly" else 1962.0,
                    step=100.0,
                    key="pc_purchases"
                )

                ending_inventory = st.number_input(
                    f"Ending Inventory (€)",
                    min_value=0.0,
                    value=3200.0,
                    step=100.0,
                    key="pc_end_inv"
                )

                food_cost = beginning_inventory + purchases - ending_inventory

                st.markdown("---")
                st.metric(f"**Total Food Cost ({period})**", f"€{food_cost:,.2f}")

            with col2:
                st.markdown("#### 👥 Labor Costs")

                wages = st.number_input(
                    f"Wages & Salaries (€)",
                    min_value=0.0,
                    value=6000.0 if period == "Monthly" else 1385.0,
                    step=100.0,
                    key="pc_wages"
                )

                benefits = st.number_input(
                    f"Benefits & Taxes (€)",
                    min_value=0.0,
                    value=1200.0 if period == "Monthly" else 277.0,
                    step=50.0,
                    key="pc_benefits",
                    help="Include payroll taxes, insurance, etc."
                )

                labor_cost = wages + benefits

                st.markdown("---")
                st.metric(f"**Total Labor Cost ({period})**", f"€{labor_cost:,.2f}")

            # Revenue input
            st.markdown("---")
            st.markdown("#### 💰 Revenue")

            revenue = st.number_input(
                f"Total Revenue ({period}) (€)",
                min_value=0.0,
                value=25000.0 if period == "Monthly" else 5769.0,
                step=100.0,
                key="pc_revenue"
            )

            if revenue > 0:
                # Calculate percentages
                food_cost_pct = (food_cost / revenue) * 100
                labor_cost_pct = (labor_cost / revenue) * 100
                prime_cost = food_cost + labor_cost
                prime_cost_pct = (prime_cost / revenue) * 100

                remaining_for_ops = revenue - prime_cost
                remaining_for_ops_pct = (remaining_for_ops / revenue) * 100

                st.markdown("---")
                st.markdown("### 📊 Prime Cost Analysis")

                # Main metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if food_cost_pct <= 30:
                        st.metric("Food Cost", f"€{food_cost:,.2f}", f"{food_cost_pct:.1f}% ✓", delta_color="normal")
                    elif food_cost_pct <= 35:
                        st.metric("Food Cost", f"€{food_cost:,.2f}", f"{food_cost_pct:.1f}%", delta_color="normal")
                    else:
                        st.metric("Food Cost", f"€{food_cost:,.2f}", f"{food_cost_pct:.1f}% ⚠", delta_color="inverse")

                with col2:
                    if labor_cost_pct <= 30:
                        st.metric("Labor Cost", f"€{labor_cost:,.2f}", f"{labor_cost_pct:.1f}% ✓", delta_color="normal")
                    elif labor_cost_pct <= 35:
                        st.metric("Labor Cost", f"€{labor_cost:,.2f}", f"{labor_cost_pct:.1f}%", delta_color="normal")
                    else:
                        st.metric("Labor Cost", f"€{labor_cost:,.2f}", f"{labor_cost_pct:.1f}% ⚠", delta_color="inverse")

                with col3:
                    if prime_cost_pct <= 60:
                        st.metric("Prime Cost", f"€{prime_cost:,.2f}", f"{prime_cost_pct:.1f}% ✓ Excellent", delta_color="normal")
                    elif prime_cost_pct <= 65:
                        st.metric("Prime Cost", f"€{prime_cost:,.2f}", f"{prime_cost_pct:.1f}% → Good", delta_color="normal")
                    else:
                        st.metric("Prime Cost", f"€{prime_cost:,.2f}", f"{prime_cost_pct:.1f}% ⚠ High", delta_color="inverse")

                with col4:
                    st.metric("Remaining for Ops", f"€{remaining_for_ops:,.2f}", f"{remaining_for_ops_pct:.1f}%")

                # Visual breakdown
                st.markdown("---")
                st.markdown("### 📊 Cost Breakdown")

                breakdown_data = pd.DataFrame({
                    'Category': ['Food Cost', 'Labor Cost', 'Remaining for Operations & Profit'],
                    'Amount': [food_cost, labor_cost, remaining_for_ops],
                    'Percentage': [food_cost_pct, labor_cost_pct, remaining_for_ops_pct]
                })

                fig = px.pie(
                    breakdown_data,
                    values='Amount',
                    names='Category',
                    title=f'{period} Cost Breakdown',
                    hole=0.4,
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

                # Recommendations
                st.markdown("---")
                st.markdown("### 💡 Recommendations")

                if prime_cost_pct <= 60:
                    st.success(f"✅ **Excellent!** Your prime cost of {prime_cost_pct:.1f}% is in the optimal range. You have €{remaining_for_ops:,.2f} ({remaining_for_ops_pct:.1f}%) remaining for other expenses and profit.")
                elif prime_cost_pct <= 65:
                    st.info(f"ℹ️ **Good!** Your prime cost of {prime_cost_pct:.1f}% is acceptable but has room for improvement. Target: <60%")

                    # Specific recommendations
                    if food_cost_pct > 35:
                        st.warning(f"**Food Cost Action Item:** Your food cost ({food_cost_pct:.1f}%) is above target. Review portion sizes, reduce waste, and negotiate with suppliers.")
                    if labor_cost_pct > 35:
                        st.warning(f"**Labor Cost Action Item:** Your labor cost ({labor_cost_pct:.1f}%) is above target. Optimize scheduling and cross-train staff.")
                else:
                    st.error(f"⚠️ **Action Needed!** Your prime cost of {prime_cost_pct:.1f}% is too high. You need to reduce by {prime_cost_pct - 60:.1f} percentage points.")

                    reduction_needed = revenue * ((prime_cost_pct - 60) / 100)
                    st.error(f"**Target:** Reduce prime cost by €{reduction_needed:,.2f} to reach 60%")

                    # Breakdown of issues
                    issues = []
                    if food_cost_pct > 35:
                        issues.append(f"🍽️ Food cost is {food_cost_pct - 35:.1f}pp above target")
                    if labor_cost_pct > 35:
                        issues.append(f"👥 Labor cost is {labor_cost_pct - 35:.1f}pp above target")

                    if issues:
                        st.markdown("**Specific Issues:**")
                        for issue in issues:
                            st.markdown(f"- {issue}")

                # Trend tracking suggestion
                st.markdown("---")
                with st.expander("📈 Track Your Prime Cost Over Time"):
                    st.markdown("""
                    **Best Practice:** Calculate Prime Cost weekly

                    **Weekly Tracking Template:**
                    1. Count inventory every Monday
                    2. Record all purchases
                    3. Track labor hours daily
                    4. Calculate Prime Cost each Sunday
                    5. Compare week-over-week

                    **Red Flags:**
                    - Prime Cost increases >2% week-over-week
                    - Food Cost spikes (check for waste/theft)
                    - Labor Cost rises (check scheduling)

                    **Pro Tip:** Use a spreadsheet to track trends and catch problems early!
                    """)

        # TARGET PRICING
        elif calc_mode == "🎯 Target Pricing":
            st.markdown("### 🎯 Target Pricing Calculator")
            st.markdown("Work backwards from your desired profit margin to find the optimal selling price.")

            with st.expander("💡 Understanding Target Pricing"):
                st.markdown("""
                **Three Pricing Strategies:**

                1. **Cost-Plus Pricing**
                   - Start with your costs
                   - Add desired markup (e.g., 3x ingredient cost)
                   - Simple but may ignore market conditions

                2. **Target Profit Margin**
                   - Decide on desired profit margin %
                   - Calculate price needed to achieve it
                   - Balances profitability with market awareness

                3. **Competitive Pricing**
                   - Match or beat competitor prices
                   - Check profitability afterwards
                   - Good for market penetration

                **Recommended Food Cost Percentages:**
                - Fine Dining: 25-30%
                - Casual Dining: 28-32%
                - Fast Casual: 30-33%
                - QSR/Fast Food: 30-35%
                - Cafes/Coffee: 20-25%
                - Bars (food): 25-30%
                """)

            st.markdown("---")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### 📝 Item Details")

                target_item_name = st.text_input(
                    "Item Name",
                    "Signature Burger",
                    key="target_name"
                )

                total_cost = st.number_input(
                    "Total Cost per Item (€)",
                    min_value=0.0,
                    value=3.50,
                    step=0.10,
                    key="target_cost",
                    help="Include all ingredients and packaging"
                )

            with col2:
                st.markdown("#### 🎯 Your Restaurant Type")
                restaurant_type = st.selectbox(
                    "Type",
                    ["Fine Dining (25-30%)", "Casual Dining (28-32%)", "Fast Casual (30-33%)", "QSR/Fast Food (30-35%)", "Cafe/Coffee Shop (20-25%)", "Custom"],
                    key="target_type"
                )

            st.markdown("---")
            st.markdown("### 💰 Pricing Strategies")

            # Strategy tabs
            strategy_tab1, strategy_tab2, strategy_tab3 = st.tabs([
                "🎯 Target Food Cost %",
                "💵 Cost Multiplier",
                "📊 Competitive Comparison"
            ])

            with strategy_tab1:
                st.markdown("#### Calculate Price Based on Desired Food Cost %")

                if "Custom" in restaurant_type:
                    target_food_cost_pct = st.slider(
                        "Target Food Cost Percentage",
                        15.0, 40.0, 30.0, 0.5,
                        key="custom_food_cost",
                        help="What % of the selling price should be food cost?"
                    )
                else:
                    # Extract range from selection
                    ranges = {
                        "Fine Dining (25-30%)": (25, 30),
                        "Casual Dining (28-32%)": (28, 32),
                        "Fast Casual (30-33%)": (30, 33),
                        "QSR/Fast Food (30-35%)": (30, 35),
                        "Cafe/Coffee Shop (20-25%)": (20, 25)
                    }
                    low, high = ranges[restaurant_type]
                    target_food_cost_pct = st.slider(
                        "Target Food Cost Percentage",
                        float(low), float(high), float((low + high) / 2), 0.5,
                        key="target_food_cost_pct",
                        help=f"Recommended range for {restaurant_type.split(' (')[0]}"
                    )

                # Calculate required price
                required_price = total_cost / (target_food_cost_pct / 100)
                profit_per_item = required_price - total_cost
                profit_margin = (profit_per_item / required_price) * 100

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Required Selling Price", f"€{required_price:.2f}")
                with col2:
                    st.metric("Profit per Item", f"€{profit_per_item:.2f}")
                with col3:
                    st.metric("Profit Margin", f"{profit_margin:.1f}%")
                with col4:
                    st.metric("Food Cost %", f"{target_food_cost_pct:.1f}%")

                # Monthly projections
                st.markdown("---")
                monthly_sales_target = st.slider(
                    "Expected Monthly Sales",
                    50, 1000, 200, 10,
                    key="target_monthly"
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Monthly Revenue", f"€{required_price * monthly_sales_target:,.2f}")
                with col2:
                    st.metric("Monthly Food Cost", f"€{total_cost * monthly_sales_target:,.2f}")
                with col3:
                    st.metric("Monthly Gross Profit", f"€{profit_per_item * monthly_sales_target:,.2f}")

                # Compare different food cost %
                st.markdown("---")
                st.markdown("#### Compare Different Food Cost Targets")

                scenarios = []
                for fc_pct in [25, 28, 30, 32, 35]:
                    price = total_cost / (fc_pct / 100)
                    profit = price - total_cost
                    scenarios.append({
                        'Food Cost %': f"{fc_pct}%",
                        'Selling Price': f"€{price:.2f}",
                        'Profit/Item': f"€{profit:.2f}",
                        'Monthly Profit': f"€{profit * monthly_sales_target:,.2f}",
                        'Markup': f"{((price / total_cost) - 1) * 100:.0f}%"
                    })

                st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)

            with strategy_tab2:
                st.markdown("#### Calculate Price Based on Cost Multiplier")
                st.markdown("Common markup strategies: 2x = 50% food cost, 3x = 33% food cost, 4x = 25% food cost")

                multiplier = st.slider(
                    "Cost Multiplier",
                    1.5, 5.0, 3.0, 0.1,
                    key="multiplier",
                    help="How many times cost should the price be?"
                )

                mult_price = total_cost * multiplier
                mult_profit = mult_price - total_cost
                mult_food_cost_pct = (total_cost / mult_price) * 100
                mult_profit_margin = (mult_profit / mult_price) * 100

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Selling Price", f"€{mult_price:.2f}")
                with col2:
                    st.metric("Profit per Item", f"€{mult_profit:.2f}")
                with col3:
                    st.metric("Food Cost %", f"{mult_food_cost_pct:.1f}%")
                with col4:
                    st.metric("Profit Margin", f"{mult_profit_margin:.1f}%")

                # Common multipliers
                st.markdown("---")
                st.markdown("#### Common Industry Multipliers")

                multipliers_data = []
                for mult in [2.0, 2.5, 3.0, 3.5, 4.0]:
                    price = total_cost * mult
                    profit = price - total_cost
                    fc_pct = (total_cost / price) * 100
                    multipliers_data.append({
                        'Multiplier': f"{mult}x",
                        'Price': f"€{price:.2f}",
                        'Profit/Item': f"€{profit:.2f}",
                        'Food Cost %': f"{fc_pct:.1f}%",
                        'Monthly Profit': f"€{profit * monthly_sales_target:,.2f}"
                    })

                st.dataframe(pd.DataFrame(multipliers_data), use_container_width=True, hide_index=True)

            with strategy_tab3:
                st.markdown("#### Compare with Competitor Prices")

                compare_category_target = st.selectbox(
                    "Category",
                    sorted(df['category'].unique()),
                    key="target_category",
                    help="Select a category to compare pricing"
                )

                competitor_items_target = df[df['category'] == compare_category_target]
                if len(competitor_items_target) > 0:
                    comp_avg = competitor_items_target['price'].mean()
                    comp_min = competitor_items_target['price'].min()
                    comp_max = competitor_items_target['price'].max()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Market Average", f"€{comp_avg:.2f}")
                    with col2:
                        st.metric("Market Range", f"€{comp_min:.2f} - €{comp_max:.2f}")
                    with col3:
                        num_competitors = len(competitor_items_target)
                        st.metric("Competitors", num_competitors)

                    # Calculate profitability at different price points
                    st.markdown("---")
                    st.markdown("#### Profitability at Different Price Points")

                    comp_scenarios = []

                    price_points = [
                        ("Match Lowest", comp_min),
                        ("10% Below Avg", comp_avg * 0.9),
                        ("Match Average", comp_avg),
                        ("10% Above Avg", comp_avg * 1.1),
                        ("Match Highest", comp_max)
                    ]

                    for label, price in price_points:
                        if price > 0:
                            profit = price - total_cost
                            fc_pct = (total_cost / price) * 100
                            margin = (profit / price) * 100
                            monthly_profit = profit * monthly_sales_target

                            comp_scenarios.append({
                                'Strategy': label,
                                'Price': f"€{price:.2f}",
                                'Profit/Item': f"€{profit:.2f}",
                                'Food Cost %': f"{fc_pct:.1f}%",
                                'Margin %': f"{margin:.1f}%",
                                'Monthly Profit': f"€{monthly_profit:,.2f}"
                            })

                    st.dataframe(pd.DataFrame(comp_scenarios), use_container_width=True, hide_index=True)

                    # Recommendation
                    st.markdown("---")
                    st.markdown("#### 💡 Recommendation")

                    # Calculate ideal price (30% food cost)
                    ideal_price = total_cost / 0.30

                    if ideal_price <= comp_avg:
                        st.success(f"✅ **Great opportunity!** Your ideal price (€{ideal_price:.2f} at 30% food cost) is below market average (€{comp_avg:.2f}). You can be competitive and profitable.")
                    elif ideal_price <= comp_avg * 1.1:
                        st.info(f"ℹ️ **Good positioning.** Your ideal price (€{ideal_price:.2f}) is slightly above average but within competitive range.")
                    else:
                        st.warning(f"⚠️ **High cost item.** Your ideal price (€{ideal_price:.2f}) is significantly above market average (€{comp_avg:.2f}). Consider reducing costs or emphasizing premium value.")

                else:
                    st.info("Select a category to see competitor pricing data.")

    with tab4:
        st.markdown("### 🤖 AI-Powered Pricing Recommendations")
        st.markdown("Get personalized pricing insights powered by Claude AI based on your costs and competitor data.")

        client = get_claude_client()

        if not client:
            st.warning("⚠️ Claude API key not configured. Set ANTHROPIC_API_KEY environment variable to enable AI recommendations.")

            with st.expander("📖 How to enable AI recommendations"):
                st.markdown("""
                **Setup Instructions:**

                1. Get your API key from [console.anthropic.com](https://console.anthropic.com)
                2. Set environment variable:
                   ```bash
                   # Windows (PowerShell)
                   $env:ANTHROPIC_API_KEY="your-api-key-here"

                   # Mac/Linux
                   export ANTHROPIC_API_KEY="your-api-key-here"
                   ```
                3. Restart Streamlit
                """)
        else:
            st.success("✅ AI recommendations enabled!")

            st.markdown("---")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("#### 📝 Your Item Details")
                ai_item_name = st.text_input(
                    "Item Name",
                    "Cappuccino",
                    key="ai_item",
                    help="The menu item you want pricing recommendations for"
                )
                ai_your_price = st.number_input(
                    "Your Selling Price (€)",
                    min_value=0.0,
                    value=3.50,
                    step=0.10,
                    key="ai_price",
                    help="Your current or proposed selling price"
                )
                ai_ingredient_cost = st.number_input(
                    "Ingredient Cost (€)",
                    min_value=0.0,
                    value=0.80,
                    step=0.10,
                    key="ai_cost",
                    help="Total cost to make this item"
                )

            with col2:
                st.markdown("#### 🔍 Market Comparison")
                ai_compare_category = st.selectbox(
                    "Category",
                    sorted(df['category'].unique()),
                    key="ai_category",
                    help="Category to compare against for AI analysis"
                )
                ai_competitor_items = df[df['category'] == ai_compare_category]

                if len(ai_competitor_items) > 0:
                    st.metric("Competitor Items", len(ai_competitor_items))
                    st.metric("Market Average", f"€{ai_competitor_items['price'].mean():.2f}")

            if st.button("🤖 Generate AI Recommendations", type="primary", help="Click to get AI-powered pricing insights"):
                with st.spinner("🧠 Analyzing your pricing with Claude AI..."):
                    recommendations = get_ai_recommendations(
                        ai_item_name,
                        ai_your_price,
                        ai_ingredient_cost,
                        ai_competitor_items,
                        ai_compare_category
                    )

                    if recommendations:
                        st.markdown("---")
                        st.markdown("### 💡 AI Analysis & Recommendations")
                        st.markdown(recommendations)

    with tab5:
        st.markdown("### 🔄 Data Collection")
        st.markdown("Collect competitor pricing data from restaurants. All scraping happens in-app - no command line needed!")

        st.markdown("---")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 📍 Data Source Configuration")

            city = st.text_input(
                "City",
                "Maastricht",
                key="scraper_city",
                help="City to collect restaurant data from"
            )

            scrape_all = st.checkbox(
                "Scrape ALL restaurants (recommended)",
                value=True,
                key="scrape_all",
                help="Scrape all available restaurants in the city. Uncheck to set a custom limit."
            )

            num_restaurants = None
            if not scrape_all:
                num_restaurants = st.number_input(
                    "Number of Restaurants",
                    min_value=1,
                    max_value=500,
                    value=50,
                    step=10,
                    key="scraper_count",
                    help="How many restaurants to scrape data from"
                )

            scraper_type = st.selectbox(
                "Data Source",
                ["Thuisbezorgd.nl"],
                key="scraper_type",
                help="Choose which sources to collect data from",
                disabled=True  # Only Thuisbezorgd for now
            )

        with col2:
            st.markdown("#### 📊 Current Data Status")

            try:
                with open('scraped_menus.json', 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
                    st.metric("Restaurants", len(current_data))
                    total_items = sum(len(r.get('menu_items', [])) for r in current_data)
                    st.metric("Menu Items", total_items)

                    # Get last update time
                    if current_data:
                        import datetime
                        last_update = current_data[0].get('scraped_at', 'Unknown')
                        st.caption(f"Last updated: {last_update[:16]}")

                    st.success("✅ Data loaded")
            except FileNotFoundError:
                st.warning("⚠️ No data yet")
                st.info("Click 'Start Collection' to gather data")

        st.markdown("---")

        st.markdown("#### 🚀 Start Data Collection")

        # Initialize session state for scraping status
        if 'scraping_in_progress' not in st.session_state:
            st.session_state.scraping_in_progress = False
        if 'scraping_complete' not in st.session_state:
            st.session_state.scraping_complete = False

        col_btn1, col_btn2 = st.columns([1, 3])

        with col_btn1:
            start_button = st.button(
                "🔄 Start Collection",
                type="primary",
                key="start_scraper",
                disabled=st.session_state.scraping_in_progress
            )

        with col_btn2:
            if st.session_state.scraping_in_progress:
                st.warning("⏳ Scraping in progress... This may take several minutes.")

        if start_button:
            st.session_state.scraping_in_progress = True
            st.session_state.scraping_complete = False

            # Create progress containers
            progress_bar = st.progress(0)
            status_text = st.empty()
            info_box = st.info("🔍 Initializing scraper...")

            try:
                # Progress callback for UI updates
                def update_progress(current, total, message):
                    progress = current / total if total > 0 else 0
                    progress_bar.progress(progress)
                    status_text.text(message)

                # Initialize scraper (headless mode for production)
                status_text.text("🚀 Starting Selenium WebDriver...")
                manager = ScraperManager(headless=True)

                # Determine max_restaurants
                max_rest = None if scrape_all else num_restaurants

                # Start scraping
                info_box.info(f"🔍 Discovering restaurants in {city}...")
                data = manager.discover_and_scrape_thuisbezorgd(
                    city=city.lower(),
                    max_restaurants=max_rest,
                    progress_callback=update_progress
                )

                # Save data
                status_text.text("💾 Saving data...")
                manager.save_to_json('scraped_menus.json')
                manager.save_to_csv('scraped_menus.csv')

                # Cleanup
                manager.close_all()

                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Complete!")

                st.success(f"""
                ✅ **Scraping Complete!**

                - **Restaurants scraped:** {len(data)}
                - **Total menu items:** {sum(r.get('total_items', 0) for r in data)}
                - **Data saved to:** `scraped_menus.json`

                You can now view the data in the Market Overview and Competitor Analysis tabs!
                """)

                st.session_state.scraping_complete = True

            except Exception as e:
                st.error(f"❌ **Error during scraping:**\n\n{str(e)}")
                st.info("💡 Try running the scraper from command line for detailed logs: `python scraper_new.py`")

            finally:
                st.session_state.scraping_in_progress = False

        st.markdown("---")

        # Custom cafe URLs section
        st.markdown("### ☕ Add Custom Cafe/Restaurant Websites")
        st.markdown("Scrape menus from individual cafe websites that aren't on Thuisbezorgd")

        with st.expander("➕ Add Custom Cafe URLs", expanded=False):
            st.markdown("""
            **Supported Website Types:**
            - ✅ Squarespace cafes (e.g., mickeybrowns.nl)
            - ✅ WordPress restaurants
            - ✅ Custom websites with menu pages
            - ✅ Any site with structured menu data

            **What Gets Scraped:**
            - Menu item names
            - Prices (if available)
            - Categories
            - Descriptions
            """)

            # Initialize session state for custom URLs
            if 'custom_urls' not in st.session_state:
                st.session_state.custom_urls = []

            # Input for new URL
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                new_url = st.text_input(
                    "Website URL",
                    placeholder="https://example.com/menu",
                    key="new_cafe_url",
                    help="Full URL to the cafe's menu page"
                )

            with col2:
                new_name = st.text_input(
                    "Cafe Name",
                    placeholder="Mickey Browns",
                    key="new_cafe_name",
                    help="Name of the cafe/restaurant"
                )

            with col3:
                st.markdown("&nbsp;")  # Spacing
                if st.button("➕ Add", type="secondary"):
                    if new_url and new_name:
                        st.session_state.custom_urls.append({
                            'url': new_url,
                            'name': new_name
                        })
                        st.success(f"Added {new_name}!")
                        st.rerun()
                    else:
                        st.error("Please enter both URL and name")

            # Display added URLs
            if st.session_state.custom_urls:
                st.markdown("---")
                st.markdown("#### 📋 Custom URLs to Scrape")

                for idx, cafe in enumerate(st.session_state.custom_urls):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.text(cafe['url'])
                    with col2:
                        st.text(cafe['name'])
                    with col3:
                        if st.button("❌", key=f"remove_cafe_{idx}"):
                            st.session_state.custom_urls.pop(idx)
                            st.rerun()

                # Scrape custom URLs button
                st.markdown("---")
                if st.button("🚀 Scrape Custom Cafes", type="primary", key="scrape_custom"):
                    st.session_state.scraping_in_progress = True

                    progress_bar_custom = st.progress(0)
                    status_text_custom = st.empty()

                    try:
                        status_text_custom.text("🚀 Starting custom cafe scraper...")
                        manager = ScraperManager(headless=True)

                        total_urls = len(st.session_state.custom_urls)

                        for idx, cafe in enumerate(st.session_state.custom_urls):
                            progress = (idx / total_urls) * 100
                            progress_bar_custom.progress(progress / 100)
                            status_text_custom.text(f"Scraping {cafe['name']} ({idx + 1}/{total_urls})...")

                            result = manager.scrape_url(cafe['url'], restaurant_name=cafe['name'])

                            if not result:
                                st.warning(f"⚠️ Could not scrape {cafe['name']} - site structure may not be compatible")

                        # Load existing data and merge
                        try:
                            with open('scraped_menus.json', 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                        except FileNotFoundError:
                            existing_data = []

                        # Merge with existing data (avoid duplicates by URL)
                        existing_urls = {r['url'] for r in existing_data}
                        for restaurant in manager.data:
                            if restaurant['url'] not in existing_urls:
                                existing_data.append(restaurant)

                        # Save combined data
                        with open('scraped_menus.json', 'w', encoding='utf-8') as f:
                            json.dump(existing_data, f, indent=2, ensure_ascii=False)

                        manager.close_all()

                        progress_bar_custom.progress(100)
                        status_text_custom.text("✅ Complete!")

                        st.success(f"""
                        ✅ **Custom Cafe Scraping Complete!**

                        - **Cafes scraped:** {len(manager.data)}
                        - **Total items extracted:** {sum(r.get('total_items', 0) for r in manager.data)}
                        - **Data merged with existing data**

                        Go to Market Overview to see your cafe data alongside Thuisbezorgd restaurants!
                        """)

                        # Clear the URLs after successful scrape
                        st.session_state.custom_urls = []

                    except Exception as e:
                        st.error(f"❌ **Error scraping custom cafes:**\n\n{str(e)}")

                    finally:
                        st.session_state.scraping_in_progress = False

            else:
                st.info("💡 Add cafe URLs above to start scraping individual websites")

        st.markdown("---")

        st.markdown("#### ℹ️ About Data Collection")

        with st.expander("How does data collection work?"):
            st.markdown("""
            **Multi-Source Data Collection:**

            **1. Thuisbezorgd.nl Platform Scraping:**
            - Scrapes ALL restaurants in the selected city (not just a sample)
            - Uses intelligent scrolling to load all available restaurants
            - Typically finds 100-300+ restaurants per city
            - Automated restaurant type classification

            **2. Custom Cafe/Restaurant Websites:**
            - **Squarespace Sites** - Specialized scraper for Squarespace-based cafes
            - **WordPress Sites** - Generic scraper handles WordPress menus
            - **Custom Sites** - Adaptive scraping for any menu structure
            - **Examples**: mickeybrowns.nl, local cafe websites, independent restaurants

            **What Data is Collected:**
            - Restaurant names and types (automatically classified)
            - Menu item names and descriptions
            - Prices (cleaned and standardized to €)
            - Categories (burgers, pizza, asian, drinks, etc.)
            - Price range classification (budget, moderate, premium, luxury)

            **Intelligent Scraping Technology:**
            - **Multiple scraper engines** - Thuisbezorgd, Squarespace, Generic
            - **Automatic routing** - System picks the best scraper for each URL
            - **Fallback strategies** - Multiple extraction methods per site
            - **Pattern recognition** - Finds menu items even on unstructured sites
            - **Text-based extraction** - Works even without structured HTML

            **Technical Details:**
            - Uses Selenium WebDriver for JavaScript-heavy sites
            - Handles infinite-scroll pages automatically
            - Cookie popup and overlay management
            - Multiple CSS selector strategies
            - Regular expression pattern matching for prices
            - Smart category detection

            **Privacy & Ethics:**
            - Only publicly available pricing data is collected
            - No personal information is stored
            - Data is used for competitive analysis only
            - Respects robots.txt and adds delays between requests
            - No aggressive scraping or server overload

            **Data Merging:**
            - Thuisbezorgd data + Custom cafe data = Complete market view
            - Duplicates automatically removed by URL
            - All sources appear together in Market Overview
            - Filter by type to see specific competitive sets
            """)

        with st.expander("Troubleshooting"):
            st.markdown("""
            **Common Issues:**

            1. **Scraping takes too long**:
               - Scraping ALL restaurants can take 30+ minutes
               - Uncheck "Scrape ALL restaurants" to set a limit
               - Each restaurant takes ~5-10 seconds to scrape

            2. **No data found**:
               - Check if the city name is correct (e.g., "maastricht", "amsterdam")
               - Try running from command line: `python scraper_new.py`

            3. **Chrome/Selenium errors**:
               - Ensure Chrome/Chromium is installed
               - Check that chromedriver is compatible with your Chrome version

            4. **Incomplete data**:
               - Some restaurants may be closed or have restricted menus
               - The scraper automatically skips failed restaurants

            **File Locations:**
            - Data (JSON): `scraped_menus.json`
            - Data (CSV): `scraped_menus.csv`
            - Scrapers: `scrapers/` directory
            - Main scraper: `scraper_manager.py`

            **Performance Tips:**
            - Use headless mode (enabled by default in-app)
            - Start with a smaller limit (~20 restaurants) to test
            - Run during off-peak hours for faster scraping
            """)

        # Show recent scraping logs if available
        if st.session_state.scraping_complete:
            with st.expander("📋 View Scraped Data Summary"):
                try:
                    with open('scraped_menus.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    st.write(f"**Total Restaurants:** {len(data)}")

                    # Create summary table
                    summary_data = []
                    for restaurant in data:
                        summary_data.append({
                            'Restaurant': restaurant['restaurant_name'],
                            'Items': restaurant['total_items'],
                            'Types': ', '.join(restaurant.get('restaurant_types', [])),
                            'Price Range': restaurant.get('price_range', 'unknown')
                        })

                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(df_summary, use_container_width=True)

                except Exception as e:
                    st.error(f"Could not load summary: {e}")

except FileNotFoundError:
    st.error("❌ No data found! Please use the Data Collection tab to gather competitor data.")
    st.info("💡 Go to the '🔄 Data Collection' tab to start collecting data, or run `python scraper.py` from command line.")

# Footer
st.markdown("---")
st.markdown("**Menu Price Optimizer** | Built for cafes and restaurants in Maastricht | Powered by Claude AI")