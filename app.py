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
        st.markdown("Get a comprehensive view of the competitive landscape in your market.")
        
        # Show data quality info if restaurants were filtered out
        if metadata['filtered_out'] > 0:
            st.info(f"ℹ️ **Data Note:** Showing {metadata['with_valid_prices']} of {metadata['total_in_file']} restaurants scraped. "
                   f"{metadata['filtered_out']} restaurants were filtered out (no menu items or missing prices). "
                   f"Re-run the scraper to collect more complete data.")

        with st.expander("ℹ️ How to use this tab"):
            st.markdown("""
            **What you'll find here:**
            - 📊 **Key Metrics**: Overview of restaurants, items, and price ranges
            - 🏷️ **Category Grid**: Visual overview of all menu categories with average prices
            - 📈 **Charts**: Price distribution, restaurant comparisons, and market insights
            - 🔍 **Filters**: Narrow down by restaurant type and price range

            **Tips:**
            - Click on category cards to see which categories have the highest prices
            - Use filters to focus on specific restaurant types or price ranges
            - Check the price distribution to see where your items fit in the market
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

        # Restaurant type and price range filters
        col1, col2 = st.columns(2)
        with col1:
            # Restaurant types filter
            all_types = set()
            for types_str in df['restaurant_types'].unique():
                all_types.update([t.strip() for t in types_str.split(',')])
            all_types = sorted(list(all_types))

            selected_type = st.selectbox(
                "Filter by Restaurant Type",
                ['All'] + all_types,
                key="overview_type_filter"
            )

        with col2:
            # Price range filter
            price_ranges = ['All'] + sorted(df['price_range'].unique().tolist())
            selected_price_range = st.selectbox(
                "Filter by Price Range",
                price_ranges,
                key="overview_price_filter"
            )

        # Apply filters
        filtered_overview_df = df.copy()
        if selected_type != 'All':
            filtered_overview_df = filtered_overview_df[
                filtered_overview_df['restaurant_types'].str.contains(selected_type, case=False, na=False)
            ]
        if selected_price_range != 'All':
            filtered_overview_df = filtered_overview_df[
                filtered_overview_df['price_range'] == selected_price_range
            ]

        if len(filtered_overview_df) == 0:
            st.warning("No restaurants match the selected filters")
            filtered_overview_df = df  # Fallback to show all data

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
        st.markdown("### 💵 Profit Margin Calculator")
        st.markdown("Calculate your profit margins and compare with competitor pricing to optimize your menu.")

        with st.expander("ℹ️ How to use this tab"):
            st.markdown("""
            **What you'll find here:**
            - 📝 **Your Item Inputs**: Enter your item details (name, price, costs)
            - 🔍 **Category Comparison**: Compare against competitor averages
            - 💰 **Profit Analysis**: See margins and positioning vs market
            - 📊 **Recommendations**: Get instant feedback on your pricing
            - 🔮 **What-If Analysis**: See how price changes affect monthly profit

            **Tips:**
            - Be accurate with ingredient costs for reliable margin calculations
            - Compare with similar categories for relevant insights
            - Use the what-if slider to model different sales volumes
            - Watch for opportunities to increase prices while staying competitive
            """)

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📝 Your Menu Item")
            item_name = st.text_input(
                "Item Name",
                "Cappuccino",
                key="calc_item",
                help="Enter the name of your menu item"
            )
            your_price = st.number_input(
                "Your Selling Price (€)",
                min_value=0.0,
                value=3.50,
                step=0.10,
                key="calc_price",
                help="The price you charge customers"
            )
            ingredient_cost = st.number_input(
                "Ingredient Cost (€)",
                min_value=0.0,
                value=0.80,
                step=0.10,
                key="calc_cost",
                help="Total cost of ingredients per item"
            )

        with col2:
            st.markdown("#### 🔍 Compare with Category")
            compare_category = st.selectbox(
                "Category",
                sorted(df['category'].unique()),
                key="calc_category",
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

            # Display results
            st.markdown("---")
            st.markdown("### 💰 Your Profit Analysis")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Profit per Item", f"€{profit_per_item:.2f}")
            with col2:
                st.metric("Profit Margin", f"{margin_percentage:.1f}%")
            with col3:
                st.metric("Competitor Avg", f"€{avg_competitor_price:.2f}")
            with col4:
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

            monthly_sales = st.slider("Estimated monthly sales", 50, 500, 200, 10, key="calc_sales")

            # Calculate scenarios
            scenarios_data = []

            # Current scenario
            scenarios_data.append({
                'Scenario': '📍 Current Price',
                'Price (€)': your_price,
                'Profit/Item (€)': profit_per_item,
                'Monthly Profit (€)': profit_per_item * monthly_sales,
                'vs Competitor': 'Your current pricing'
            })

            # Match competitor average
            if avg_competitor_price > 0:
                new_profit = avg_competitor_price - ingredient_cost
                diff = (new_profit * monthly_sales) - (profit_per_item * monthly_sales)
                scenarios_data.append({
                    'Scenario': '🎯 Match Market Avg',
                    'Price (€)': avg_competitor_price,
                    'Profit/Item (€)': new_profit,
                    'Monthly Profit (€)': new_profit * monthly_sales,
                    'vs Competitor': f"+€{diff:.2f}/month" if diff > 0 else f"€{diff:.2f}/month"
                })

            # 10% increase
            increased_price = your_price * 1.1
            increased_profit = increased_price - ingredient_cost
            diff_10 = (increased_profit * monthly_sales) - (profit_per_item * monthly_sales)
            scenarios_data.append({
                'Scenario': '📈 +10% Increase',
                'Price (€)': increased_price,
                'Profit/Item (€)': increased_profit,
                'Monthly Profit (€)': increased_profit * monthly_sales,
                'vs Competitor': f"+€{diff_10:.2f}/month"
            })

            scenarios_df = pd.DataFrame(scenarios_data)
            scenarios_df['Price (€)'] = scenarios_df['Price (€)'].apply(lambda x: f"{x:.2f}")
            scenarios_df['Profit/Item (€)'] = scenarios_df['Profit/Item (€)'].apply(lambda x: f"{x:.2f}")
            scenarios_df['Monthly Profit (€)'] = scenarios_df['Monthly Profit (€)'].apply(lambda x: f"{x:.2f}")

            st.dataframe(scenarios_df, use_container_width=True, hide_index=True)

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
        st.markdown("Collect competitor pricing data from Maastricht restaurants. All inputs are managed here - no command line needed!")

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

            num_restaurants = st.number_input(
                "Number of Restaurants",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key="scraper_count",
                help="How many restaurants to scrape data from"
            )

            scraper_type = st.selectbox(
                "Data Source",
                ["Thuisbezorgd.nl", "Generic Websites", "Both"],
                key="scraper_type",
                help="Choose which sources to collect data from"
            )

        with col2:
            st.markdown("#### 📊 Current Data Status")

            try:
                with open('scraped_menus.json', 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
                    st.metric("Restaurants", len(current_data))
                    total_items = sum(len(r.get('menu_items', [])) for r in current_data)
                    st.metric("Menu Items", total_items)
                    st.success("✅ Data loaded")
            except FileNotFoundError:
                st.warning("⚠️ No data yet")
                st.info("Click 'Start Collection' to gather data")

        st.markdown("---")

        st.markdown("#### 🚀 Start Data Collection")

        if st.button("🔄 Start Collection", type="primary", key="start_scraper"):
            st.info("🔄 Data collection feature coming soon!")
            st.markdown("""
            **For now, please use the command line:**

            ```bash
            python scraper.py
            ```

            This will collect competitor pricing data and save it to `scraped_menus.json`.

            **Note:** This feature will be fully integrated in the next update, allowing you to:
            - ✅ Configure scraping parameters from the UI
            - ✅ Monitor progress in real-time
            - ✅ View collection logs
            - ✅ Refresh data with one click
            """)

        st.markdown("---")

        st.markdown("#### ℹ️ About Data Collection")

        with st.expander("How does data collection work?"):
            st.markdown("""
            **Data Sources:**
            - **Thuisbezorgd.nl**: Popular food delivery platform in the Netherlands
            - **Generic Websites**: Direct restaurant websites using AI-powered scraping

            **What data is collected:**
            - Restaurant names and types
            - Menu item names and descriptions
            - Prices
            - Categories (automatically classified)

            **Privacy & Ethics:**
            - Only publicly available pricing data is collected
            - No personal information is stored
            - Data is used for competitive analysis only
            """)

        with st.expander("Troubleshooting"):
            st.markdown("""
            **Common Issues:**

            1. **No data found**: Run `python scraper.py` from command line
            2. **Old data**: Re-run scraper to refresh
            3. **Missing restaurants**: Increase the number of restaurants to scrape

            **File Locations:**
            - Data: `scraped_menus.json`
            - Scrapers: `scrapers/` directory
            """)

except FileNotFoundError:
    st.error("❌ No data found! Please use the Data Collection tab to gather competitor data.")
    st.info("💡 Go to the '🔄 Data Collection' tab to start collecting data, or run `python scraper.py` from command line.")

# Footer
st.markdown("---")
st.markdown("**Menu Price Optimizer** | Built for cafes and restaurants in Maastricht | Powered by Claude AI")