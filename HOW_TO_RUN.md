# How to Run the Menu Price Optimizer

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the App**
   ```bash
   streamlit run app.py
   ```

3. **View in Browser**
   - The app will automatically open in your browser at `http://localhost:8501`
   - If it doesn't open automatically, navigate to that URL manually

## What You'll See

### 🎨 New UI Features (Just Added!)

1. **📊 Market Overview Tab**
   - Visual category grid showing ALL categories at a glance
   - Interactive category cards with hover effects
   - Comprehensive help section explaining features

2. **🔍 Competitor Analysis Tab**
   - NEW: Multi-select for categories (compare multiple at once!)
   - Green tags for selected categories
   - Better organized statistics

3. **💵 Profit Calculator Tab**
   - Helpful tooltips on every input field
   - Clear guidance on what to enter

4. **🤖 AI Recommendations Tab**
   - Collapsible help sections
   - Market comparison metrics

5. **🔄 Data Collection Tab (NEW!)**
   - All scraper inputs now in the UI
   - Current data status display
   - Help and troubleshooting sections

### 🎯 Smooth Tab Switching
- Tabs now have smooth cubic-bezier animations
- Hover effects lift tabs slightly
- Active tab has a prominent green border
- All transitions are buttery smooth!

## About Your Data

**Current Status:**
- ✅ 10 restaurants scraped
- ⚠️ Only 4 have valid pricing data
- 📊 27 menu items with prices

**Restaurants with prices:**
1. Pitology (7 items)
2. Tasty Thai (8 items)
3. Chinees restaurant Chi (5 items)
4. Seven Spices Maastricht (7 items)

**To get more data:**
- Run `python scraper.py` to collect fresh data
- Or use the new Data Collection tab (UI coming soon!)

## Troubleshooting

**App not loading?**
- Make sure you installed dependencies: `pip install -r requirements_streamlit.txt`
- Check that you're in the project directory
- Try: `streamlit run app.py --server.port 8501`

**Only seeing old UI?**
- Hard refresh your browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
- Clear browser cache
- Stop and restart Streamlit

**API Key for AI Recommendations:**
```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY="your-key-here"
```

## What Changed

The UI improvements are in `app.py`. To see them, you MUST run the Streamlit app - just viewing the Python file won't show you the interface!

All changes have been committed to: `claude/improve-ui-tabs-01RJAUrpRrvPvotDVUBAHUDs`
