# Google Maps Places Scraper

A robust Python-based scraper for extracting detailed information from Google Maps places using Selenium.

## Why This Approach?

Your browser extension was blocked because:
1. **Script injection detection** - Google Maps detects `executeScript` calls
2. **Missing proper delays** - Too fast scraping triggers anti-bot measures
3. **Limited control** - Browser extensions can't fully simulate human behavior

This Python solution uses **Selenium** which:
- ✅ Opens a real Chrome browser that looks like a human user
- ✅ Can handle dynamic content and JavaScript
- ✅ Allows proper delays and scrolling
- ✅ Extracts ALL available information from detail pages

## Features

This scraper extracts:
- ✅ **Basic Info**: Name, rating, review count, category
- ✅ **Contact**: Address, phone, website
- ✅ **Details**: Business hours, price level, description
- ✅ **Attributes**: Wheelchair accessible, outdoor seating, etc.
- ✅ **Location**: Plus codes, coordinates (from URL)
- ✅ **Popular times**: When available

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ChromeDriver

**Option A - Automatic (Recommended):**
```python
# The script will auto-download ChromeDriver using webdriver-manager
# Just run the script and it handles everything
```

**Option B - Manual:**
1. Download ChromeDriver: https://chromedriver.chromium.org/downloads
2. Match your Chrome browser version
3. Add to PATH or place in project folder

### 3. Verify Chrome Browser is Installed
Make sure you have Google Chrome installed on your system.

## Usage

### Basic Usage

```bash
python google_maps_scraper.py
```

Then:
1. Paste your Google Maps search URL when prompted
2. Optionally set max places to scrape
3. Watch the scraper work!
4. Results saved to `google_places.csv` and `google_places.json`

### How to Get Search URL

1. Go to Google Maps
2. Search for what you want (e.g., "restaurants in New York")
3. Copy the URL from your browser
4. Paste it into the script

Example URLs:
```
https://www.google.com/maps/search/coffee+shops+san+francisco
https://www.google.com/maps/search/restaurants+near+times+square
https://www.google.com/maps/search/gyms+in+los+angeles
```

### Advanced Usage (Custom Script)

```python
from google_maps_scraper import GoogleMapsScraper

# Initialize scraper
scraper = GoogleMapsScraper(headless=False)  # Set True to hide browser

try:
    # Scrape places
    scraper.scrape_search_results(
        search_url="https://www.google.com/maps/search/pizza+near+me",
        max_places=50  # Limit to 50 places
    )
    
    # Save results
    scraper.save_to_csv('my_results.csv')
    scraper.save_to_json('my_results.json')
    
finally:
    scraper.close()
```

## Customization

### Modify Extracted Fields

Edit the `extract_place_details()` method in `google_maps_scraper.py`:

```python
place_data = {
    'url': url,
    'name': self.safe_extract('h1.DUwDvf'),
    'rating': self.safe_extract('div.F7nice span[aria-hidden="true"]'),
    # Add more fields here with their CSS selectors
    'your_field': self.safe_extract('your.css.selector'),
}
```

### Adjust Scraping Speed

Change delays in the script:
- `time.sleep(3)` after loading each place
- `time.sleep(2)` between places
- Increase delays if you're getting blocked

### Change Number of Scrolls

In `scrape_search_results()`:
```python
self.scroll_results_panel(scrolls=8)  # Change this number
```

## Tips for Success

1. **Don't scrape too fast** - Use reasonable delays (2-5 seconds)
2. **Don't scrape too much** - Limit to 50-100 places per session
3. **Use headless mode** - Set `headless=True` for faster, hidden scraping
4. **Rotate IPs** - Use VPN if scraping large amounts
5. **Check robots.txt** - Be respectful of Google's terms

## Troubleshooting

### "ChromeDriver not found"
- Install ChromeDriver or let webdriver-manager handle it
- Make sure Chrome browser is installed

### "Element not found" errors
- Google Maps updated their HTML structure
- Update CSS selectors in `extract_place_details()`
- Check the browser to see the current selectors

### Getting blocked/rate limited
- Increase delays between requests
- Reduce number of places scraped per session
- Use headless mode
- Add random delays: `time.sleep(random.uniform(2, 5))`

### No results found
- Check if the search URL is correct
- Make sure places are visible on the map
- Try scrolling more times

## Legal & Ethical Considerations

⚠️ **Important**: Web scraping may violate Google's Terms of Service. Use this tool responsibly:
- For personal research and analysis
- With reasonable rate limits
- Without commercial redistribution
- Respecting Google's resources

## Output Format

### CSV Output
All fields in columns, one place per row. Easy to open in Excel or Google Sheets.

### JSON Output
Structured data format, preserves nested information, good for further processing.

## Example Output

```csv
name,rating,review_count,category,address,phone,website,...
"Joe's Coffee Shop","4.5","250 reviews","Coffee shop","123 Main St, SF","(555) 123-4567","http://joescoffee.com",...
```

## License

This is a tool for educational purposes. Use responsibly and in accordance with applicable laws and terms of service.
