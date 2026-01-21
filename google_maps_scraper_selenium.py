"""
Google Maps Places Scraper
This scraper uses Selenium to automate browsing Google Maps and extract place details.
"""

import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class GoogleMapsScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome webdriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.all_places_data = []
    
    def scroll_results_panel(self, scrolls=5):
        """Scroll the results panel to load more places"""
        try:
            # Find the scrollable results container
            scrollable_div = self.driver.find_element(
                By.CSS_SELECTOR, 
                'div[role="feed"]'
            )
            
            print(f"Scrolling results panel {scrolls} times...")
            for i in range(scrolls):
                self.driver.execute_script(
                    'arguments[0].scrollTo(0, arguments[0].scrollHeight)', 
                    scrollable_div
                )
                time.sleep(2)  # Wait for content to load
                print(f"  Scroll {i+1}/{scrolls} complete")
            
            print("Scrolling complete!")
        except NoSuchElementException:
            print("Could not find scrollable results panel")
    
    def get_place_links(self):
        """Get all place links from the current results"""
        try:
            # Wait for results to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/maps/place/"]'))
            )
            
            # Find all place links
            place_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'a[href*="/maps/place/"]'
            )
            
            # Extract unique URLs
            urls = list(set([elem.get_attribute('href') for elem in place_elements if elem.get_attribute('href')]))
            print(f"Found {len(urls)} unique places")
            return urls
        
        except TimeoutException:
            print("Timeout waiting for place results")
            return []
    
    def extract_place_details(self, url):
        """Navigate to a place and extract all available details"""
        try:
            print(f"\nExtracting details from: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(3)
            
            place_data = {
                'url': url,
                'name': self.safe_extract('h1.DUwDvf'),
                'rating': self.safe_extract('div.F7nice span[aria-hidden="true"]'),
                'review_count': self.safe_extract('div.F7nice span[aria-label*="reviews"]'),
                'category': self.safe_extract('button[jsaction*="category"]'),
                'address': self.safe_extract('button[data-item-id="address"]'),
                'website': self.safe_extract_attribute('a[data-item-id="authority"]', 'href'),
                'phone': self.safe_extract('button[data-item-id*="phone"]'),
                'plus_code': self.safe_extract('button[data-item-id="oloc"]'),
                'hours': self.extract_hours(),
                'price_level': self.safe_extract('span[aria-label*="Price"]'),
                'description': self.safe_extract('div.PYvSYb'),
            }
            
            # Extract additional attributes (e.g., "Wheelchair accessible", "Outdoor seating")
            place_data['attributes'] = self.extract_attributes()
            
            # Try to get popular times if visible
            place_data['popular_times'] = self.extract_popular_times()
            
            print(f"  ✓ Extracted: {place_data['name']}")
            return place_data
        
        except Exception as e:
            print(f"  ✗ Error extracting details: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def safe_extract(self, selector, multiple=False):
        """Safely extract text from element(s)"""
        try:
            if multiple:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                return [elem.text.strip() for elem in elements if elem.text.strip()]
            else:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
        except NoSuchElementException:
            return "" if not multiple else []
    
    def safe_extract_attribute(self, selector, attribute):
        """Safely extract attribute from element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except NoSuchElementException:
            return ""
    
    def extract_hours(self):
        """Extract business hours"""
        try:
            # Click on hours button to expand if needed
            hours_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                'button[data-item-id*="hours"]'
            )
            hours_text = hours_button.get_attribute('aria-label')
            return hours_text
        except NoSuchElementException:
            return ""
    
    def extract_attributes(self):
        """Extract attributes like 'Wheelchair accessible', 'Outdoor seating', etc."""
        try:
            # Look for attribute sections
            attributes = self.safe_extract(
                'div.LTs0Rc div.fontBodyMedium',
                multiple=True
            )
            return ' | '.join(attributes) if attributes else ""
        except Exception:
            return ""
    
    def extract_popular_times(self):
        """Extract popular times information"""
        try:
            popular = self.safe_extract('div.g2BVhd div.C7xf8b')
            return popular if popular else ""
        except Exception:
            return ""
    
    def scrape_search_results(self, search_url, max_places=None):
        """
        Main method to scrape all places from a Google Maps search
        
        Args:
            search_url: The Google Maps search URL
            max_places: Maximum number of places to scrape (None for all)
        """
        print(f"Opening search URL: {search_url}\n")
        self.driver.get(search_url)
        
        # Wait for initial results to load
        time.sleep(5)
        
        # Scroll to load more results
        self.scroll_results_panel(scrolls=8)
        
        # Get all place URLs
        place_urls = self.get_place_links()
        
        if max_places:
            place_urls = place_urls[:max_places]
        
        print(f"\n{'='*60}")
        print(f"Extracting details from {len(place_urls)} places...")
        print(f"{'='*60}")
        
        # Extract details from each place
        for i, url in enumerate(place_urls, 1):
            print(f"\n[{i}/{len(place_urls)}]", end=" ")
            place_data = self.extract_place_details(url)
            self.all_places_data.append(place_data)
            time.sleep(2)  # Be respectful with requests
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Extracted {len(self.all_places_data)} places")
        print(f"{'='*60}\n")
    
    def save_to_csv(self, filename='google_places.csv'):
        """Save scraped data to CSV"""
        if not self.all_places_data:
            print("No data to save!")
            return
        
        # Get all unique keys from all dictionaries
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
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Example usage"""
    # Example: Scraping coffee shops in San Francisco
    # You should paste the Google Maps search URL here
    search_url = input("Paste your Google Maps search URL: ").strip()
    
    if not search_url:
        print("No URL provided. Using example...")
        search_url = "https://www.google.com/maps/search/coffee+shops+san+francisco"
    
    max_places = input("Max places to scrape (press Enter for all): ").strip()
    max_places = int(max_places) if max_places.isdigit() else None
    
    # Initialize scraper
    scraper = GoogleMapsScraper(headless=False)  # Set to True to hide browser
    
    try:
        # Scrape places
        scraper.scrape_search_results(search_url, max_places=max_places)
        
        # Save results
        scraper.save_to_csv('google_places.csv')
        scraper.save_to_json('google_places.json')
        
    finally:
        # Always close the browser
        scraper.close()


if __name__ == "__main__":
    main()