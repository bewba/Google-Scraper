"""
Google Maps Places Scraper - Playwright Version
Alternative to Selenium - often better at avoiding detection
"""

import asyncio
import csv
import json
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class GoogleMapsScraperPlaywright:
    def __init__(self, headless=False):
        """Initialize the scraper"""
        self.headless = headless
        self.all_places_data = []
        self.browser = None
        self.page = None
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with anti-detection measures
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create context with realistic user agent
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
    
    async def scroll_results_panel(self, scrolls=5):
        """Scroll the results panel to load more places"""
        try:
            print(f"Scrolling results panel {scrolls} times...")
            
            for i in range(scrolls):
                # Find and scroll the results feed
                await self.page.evaluate('''
                    () => {
                        const feed = document.querySelector('div[role="feed"]');
                        if (feed) {
                            feed.scrollTo(0, feed.scrollHeight);
                        }
                    }
                ''')
                await asyncio.sleep(2)
                print(f"  Scroll {i+1}/{scrolls} complete")
            
            print("Scrolling complete!")
            
        except Exception as e:
            print(f"Could not scroll results panel: {e}")
    
    async def get_place_links(self):
        """Get all place links from the current results"""
        try:
            # Wait for results to load
            await self.page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)
            
            # Extract all place URLs
            urls = await self.page.evaluate('''
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/maps/place/"]'));
                    const urls = links
                        .map(link => link.href)
                        .filter(href => href && href.includes('/maps/place/'));
                    return [...new Set(urls)];
                }
            ''')
            
            print(f"Found {len(urls)} unique places")
            return urls
        
        except PlaywrightTimeout:
            print("Timeout waiting for place results")
            return []
    
    async def extract_place_details(self, url):
        """Navigate to a place and extract all available details"""
        try:
            print(f"\nExtracting details from: {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Extract data using JavaScript
            place_data = await self.page.evaluate('''
                () => {
                    const getText = (selector) => {
                        const el = document.querySelector(selector);
                        return el ? el.textContent.trim() : '';
                    };
                    
                    const getAttribute = (selector, attr) => {
                        const el = document.querySelector(selector);
                        return el ? el.getAttribute(attr) : '';
                    };
                    
                    const getTexts = (selector) => {
                        const elements = document.querySelectorAll(selector);
                        return Array.from(elements).map(el => el.textContent.trim()).filter(Boolean);
                    };
                    
                    return {
                        name: getText('h1.DUwDvf'),
                        rating: getText('div.F7nice span[aria-hidden="true"]'),
                        review_count: getText('div.F7nice span[aria-label*="reviews"]') || getText('div.F7nice button[aria-label*="reviews"]'),
                        category: getText('button[jsaction*="category"]'),
                        address: getText('button[data-item-id="address"] div.fontBodyMedium') || getText('button[data-item-id="address"]'),
                        website: getAttribute('a[data-item-id="authority"]', 'href'),
                        phone: getText('button[data-item-id*="phone"] div.fontBodyMedium') || getText('button[data-item-id*="phone"]'),
                        plus_code: getText('button[data-item-id="oloc"] div.fontBodyMedium'),
                        hours: getAttribute('button[data-item-id*="hours"]', 'aria-label'),
                        price_level: getText('span[aria-label*="Price"]'),
                        description: getText('div.PYvSYb'),
                        attributes: getTexts('div.LTs0Rc div.fontBodyMedium').join(' | '),
                        popular_times: getText('div.g2BVhd div.C7xf8b')
                    };
                }
            ''')
            
            place_data['url'] = url
            
            print(f"  ✓ Extracted: {place_data['name']}")
            return place_data
        
        except Exception as e:
            print(f"  ✗ Error extracting details: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    async def scrape_search_results(self, search_url, max_places=None):
        """
        Main method to scrape all places from a Google Maps search
        
        Args:
            search_url: The Google Maps search URL
            max_places: Maximum number of places to scrape (None for all)
        """
        await self.init_browser()
        
        print(f"Opening search URL: {search_url}\n")
        await self.page.goto(search_url, wait_until='networkidle', timeout=30000)
        
        # Wait for initial results to load
        await asyncio.sleep(5)
        
        # Scroll to load more results
        await self.scroll_results_panel(scrolls=8)
        
        # Get all place URLs
        place_urls = await self.get_place_links()
        
        if max_places:
            place_urls = place_urls[:max_places]
        
        print(f"\n{'='*60}")
        print(f"Extracting details from {len(place_urls)} places...")
        print(f"{'='*60}")
        
        # Extract details from each place
        for i, url in enumerate(place_urls, 1):
            print(f"\n[{i}/{len(place_urls)}]", end=" ")
            place_data = await self.extract_place_details(url)
            self.all_places_data.append(place_data)
            await asyncio.sleep(2)  # Be respectful with requests
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Extracted {len(self.all_places_data)} places")
        print(f"{'='*60}\n")
    
    def save_to_csv(self, filename='google_places.csv'):
        """Save scraped data to CSV"""
        if not self.all_places_data:
            print("No data to save!")
            return
        
        # Get all unique keys
        all_keys = set()
        for place in self.all_places_data:
            all_keys.update(place.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_places_data)
        
        print(f"✓ Data saved to {filename}")
    
    def save_to_json(self, filename='google_places.json'):
        """Save scraped data to JSON"""
        if not self.all_places_data:
            print("No data to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.all_places_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to {filename}")
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    """Example usage"""
    search_url = input("Paste your Google Maps search URL: ").strip()
    
    if not search_url:
        print("No URL provided. Using example...")
        search_url = "https://www.google.com/maps/search/coffee+shops+manila"
    
    max_places = input("Max places to scrape (press Enter for all): ").strip()
    max_places = int(max_places) if max_places.isdigit() else None
    
    # Initialize scraper
    scraper = GoogleMapsScraperPlaywright(headless=False)
    
    try:
        # Scrape places
        await scraper.scrape_search_results(search_url, max_places=max_places)
        
        # Save results
        scraper.save_to_csv('google_places.csv')
        scraper.save_to_json('google_places.json')
        
    finally:
        # Always close the browser
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())