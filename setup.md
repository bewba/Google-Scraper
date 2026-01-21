# Complete Setup Guide - Google Maps Scraper

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python
- Download Python 3.8+ from https://www.python.org/downloads/
- During installation, **CHECK "Add Python to PATH"**
- Verify: Open terminal/cmd and run `python --version`

### Step 2: Install Dependencies
Open terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

For Playwright version, also run:
```bash
playwright install chromium
```

### Step 3: Run the Scraper
```bash
python quick_start.py
```

That's it! Follow the prompts.

---

## 📋 Detailed Setup

### Option 1: Selenium Version (Recommended for beginners)
✅ Automatic ChromeDriver installation
✅ Uses your existing Chrome browser
✅ Simple to set up

**Run:**
```bash
python quick_start.py
```

### Option 2: Playwright Version (Better anti-detection)
✅ Better at avoiding detection
✅ More reliable
✅ Requires one extra setup step

**Setup:**
```bash
pip install playwright
playwright install chromium
```

**Run:**
```bash
python google_maps_scraper_playwright.py
```

---

## 🎯 Usage Examples

### Example 1: Restaurants in Manila
```python
from google_maps_scraper import GoogleMapsScraper

scraper = GoogleMapsScraper(headless=False)
scraper.scrape_search_results(
    "https://www.google.com/maps/search/restaurants+manila",
    max_places=50
)
scraper.save_to_csv('restaurants.csv')
scraper.close()
```

### Example 2: Coffee Shops in BGC
```python
from google_maps_scraper import GoogleMapsScraper

scraper = GoogleMapsScraper(headless=True)  # Hidden browser
scraper.scrape_search_results(
    "https://www.google.com/maps/search/coffee+shops+bgc+taguig",
    max_places=30
)
scraper.save_to_csv('bgc_coffee.csv')
scraper.close()
```

### Example 3: Gyms in Makati
```bash
# Just use the quick start script
python quick_start.py

# Then paste: https://www.google.com/maps/search/gyms+makati
# Enter max: 20
```

---

## 🔧 Customization

### Extract Additional Fields

Edit `google_maps_scraper.py`, find the `extract_place_details()` method:

```python
place_data = {
    'url': url,
    'name': self.safe_extract('h1.DUwDvf'),
    'rating': self.safe_extract('div.F7nice span[aria-hidden="true"]'),
    
    # Add your custom fields here:
    'your_field_name': self.safe_extract('your.css.selector'),
}
```

### How to Find CSS Selectors:
1. Open Google Maps place page
2. Right-click the element you want → "Inspect"
3. In DevTools, right-click the highlighted HTML → Copy → Copy selector
4. Use that selector in your code

### Adjust Delays
```python
# In scrape_search_results()
await asyncio.sleep(2)  # Change this number (seconds)

# In scroll_results_panel()
await asyncio.sleep(2)  # Change this number (seconds)
```

---

## ❓ Troubleshooting

### "pip not found"
- Python wasn't added to PATH
- Reinstall Python and check "Add to PATH"
- Or use: `python -m pip install -r requirements.txt`

### "ChromeDriver version mismatch"
The selenium version uses `webdriver-manager` which auto-downloads the correct version. If you still have issues:
```bash
pip install --upgrade webdriver-manager
```

### "No such element" errors
Google Maps updated their HTML. Update selectors:
1. Open a place page in Google Maps
2. Right-click element → Inspect
3. Copy the CSS selector
4. Update in code

### Rate Limited / Blocked
- Increase delays: Change `time.sleep(2)` to `time.sleep(5)`
- Reduce max places per session
- Use VPN or rotate IP
- Use headless=False to appear more human-like

### Browser opens but nothing happens
- Check your internet connection
- Try a different search URL
- Increase timeout values in code
- Clear browser cache

---

## 📊 Output Files

### CSV Format
```csv
name,rating,review_count,category,address,phone,website
"Restaurant Name","4.5","123 reviews","Restaurant","123 St","555-1234","http://..."
```

Open with:
- Microsoft Excel
- Google Sheets
- Any spreadsheet software
- Python pandas: `pd.read_csv('google_places.csv')`

### JSON Format
```json
[
  {
    "name": "Restaurant Name",
    "rating": "4.5",
    "review_count": "123 reviews",
    ...
  }
]
```

Use with:
- Any programming language
- APIs
- Data processing tools

---

## ⚖️ Legal & Ethics

**Important:** Web scraping may violate Terms of Service. Use responsibly:

✅ **DO:**
- Personal research
- Small-scale data collection
- Reasonable delays between requests
- Respect robots.txt

❌ **DON'T:**
- Commercial redistribution
- High-frequency scraping
- Ignore rate limits
- Sell scraped data

**Recommendation:** Use the official Google Places API for commercial projects.

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| ChromeDriver error | Uses webdriver-manager, should auto-fix |
| No results found | Check URL, try scrolling more |
| Browser crashes | Reduce max_places, increase delays |
| Data incomplete | Google changed HTML, update selectors |

---

## 💡 Pro Tips

1. **Start small** - Test with 10 places first
2. **Use headless mode** - Faster for large scrapes
3. **Save incrementally** - Modify code to save after each place
4. **Use try-except** - Handle errors gracefully
5. **Monitor logs** - Watch for patterns in failures
6. **Respect limits** - Don't scrape thousands at once

---

## 📞 Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify all dependencies are installed
3. Try the alternative Playwright version
4. Check if Google Maps HTML has changed

---

## 🔄 Updates

To update the scraper:
```bash
git pull
pip install -r requirements.txt --upgrade
```

---

Happy scraping! 🎉