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
    
    /* Tab styling - Clean and minimal */
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
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF;
        background-color: #1A1A1A;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #FFFFFF;
        border-bottom: 2px solid #1DB954;
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

    # Convert to DataFrame
    rows = []
    for restaurant in data:
        for item in restaurant['menu_items']:
            rows.append({
                'restaurant': restaurant['restaurant_name'],
                'item_name': item['name'],
                'category': item['category'],
                'price': item['price']
            })

    df = pd.DataFrame(rows)
    # Filter out zero prices
    df = df[df['price'] > 0]
    return df

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
    df = load_data()

    # Better navigation with tabs instead of sidebar radio
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Market Overview",
        "🔍 Competitor Analysis",
        "💵 Profit Calculator",
        "🤖 AI Recommendations"
    ])

    with tab1:
        st.markdown("### Market Overview - Maastricht Restaurants")

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

        # Price distribution
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Price Distribution")
            fig = px.histogram(df, x='price', nbins=15,
                             labels={'price': 'Price (€)', 'count': 'Number of Items'},
                             color_discrete_sequence=['#667eea'])
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Average Price by Restaurant")
            restaurant_avg = df.groupby('restaurant')['price'].mean().sort_values(ascending=False)
            fig = px.bar(x=restaurant_avg.values, y=restaurant_avg.index,
                        orientation='h',
                        labels={'x': 'Average Price (€)', 'y': ''},
                        color=restaurant_avg.values,
                        color_continuous_scale='Viridis')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Category breakdown
        st.markdown("#### Prices by Category")
        category_stats = df.groupby('category').agg({
            'price': ['mean', 'min', 'max', 'count']
        }).round(2)
        category_stats.columns = ['Avg Price (€)', 'Min Price (€)', 'Max Price (€)', 'Items']
        category_stats = category_stats.sort_values('Avg Price (€)', ascending=False)
        st.dataframe(category_stats, use_container_width=True)

    with tab2:
        st.markdown("### Competitor Analysis")

        # Select category to analyze
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filter by Category", categories, key="comp_category")

        if selected_category != 'All':
            filtered_df = df[df['category'] == selected_category]
        else:
            filtered_df = df

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
        st.markdown("Calculate your profit margins and compare with competitor pricing")

        st.markdown("---")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### Your Menu Item")
            item_name = st.text_input("Item Name", "Cappuccino", key="calc_item")
            your_price = st.number_input("Your Selling Price (€)", min_value=0.0, value=3.50, step=0.10, key="calc_price")
            ingredient_cost = st.number_input("Ingredient Cost (€)", min_value=0.0, value=0.80, step=0.10, key="calc_cost")

        with col2:
            st.markdown("#### Compare with Category")
            compare_category = st.selectbox("Category", sorted(df['category'].unique()), key="calc_category")

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

        client = get_claude_client()

        if not client:
            st.warning("⚠️ Claude API key not configured. Set ANTHROPIC_API_KEY environment variable to enable AI recommendations.")
            st.markdown("""
            **To enable AI recommendations:**
            
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
                ai_item_name = st.text_input("Item Name", "Cappuccino", key="ai_item")
                ai_your_price = st.number_input("Your Selling Price (€)", min_value=0.0, value=3.50, step=0.10, key="ai_price")
                ai_ingredient_cost = st.number_input("Ingredient Cost (€)", min_value=0.0, value=0.80, step=0.10, key="ai_cost")

            with col2:
                ai_compare_category = st.selectbox("Category", sorted(df['category'].unique()), key="ai_category")
                ai_competitor_items = df[df['category'] == ai_compare_category]

            if st.button("🤖 Generate AI Recommendations", type="primary"):
                with st.spinner("Analyzing your pricing with Claude AI..."):
                    recommendations = get_ai_recommendations(
                        ai_item_name,
                        ai_your_price,
                        ai_ingredient_cost,
                        ai_competitor_items,
                        ai_compare_category
                    )

                    if recommendations:
                        st.markdown("---")
                        st.markdown("### 💡 AI Analysis")
                        st.markdown(recommendations)

except FileNotFoundError:
    st.error("❌ No data found! Please run the scraper first to generate scraped_menus.json")
    st.info("Run: `python scraper.py` to collect competitor data")

# Footer
st.markdown("---")
st.markdown("**Menu Price Optimizer** | Built for cafes and restaurants in Maastricht | Powered by Claude AI")