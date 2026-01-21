"""
Quick Start Script for Google Maps Scraper
Just run this file and follow the prompts!
"""

from google_maps_scraper_selenium import GoogleMapsScraper
from csv_generator import save_clean_csv

def main():
    print("=" * 70)
    print("GOOGLE MAPS PLACES SCRAPER")
    print("=" * 70)
    print()
    
    # Get search URL from user
    print("Step 1: Get your Google Maps search URL")
    print("-" * 70)
    print("1. Go to Google Maps (https://maps.google.com)")
    print("2. Search for what you want (e.g., 'restaurants in Manila')")
    print("3. Copy the URL from your browser")
    print("4. Paste it below")
    print()
    
    search_url = input("Paste your Google Maps search URL here: ").strip()
    
    if not search_url or 'google.com/maps' not in search_url:
        print("\n❌ Invalid URL. Using example URL instead...")
        search_url = "https://www.google.com/maps/search/restaurants+manila"
        print(f"Using: {search_url}")
    
    print()
    
    # Get max places
    print("Step 2: How many places to scrape?")
    print("-" * 70)
    max_input = input("Enter max number (or press Enter for all visible places): ").strip()
    max_places = int(max_input) if max_input.isdigit() else None
    
    if max_places:
        print(f"Will scrape up to {max_places} places")
    else:
        print("Will scrape all visible places (may take a while!)")
    
    print()
    
    # Ask about headless mode
    print("Step 3: Browser visibility")
    print("-" * 70)
    headless_input = input("Hide browser window? (y/n, default=n): ").strip().lower()
    headless = headless_input == 'y'
    
    if headless:
        print("Browser will run in background (headless mode)")
    else:
        print("Browser will be visible so you can watch the scraping")
    
    print()
    print("=" * 70)
    print("STARTING SCRAPER...")
    print("=" * 70)
    print()
    
    # Initialize scraper
    scraper = GoogleMapsScraper(headless=headless)
    
    try:
        # Scrape places
        scraper.scrape_search_results(search_url, max_places=max_places)
        
        # Save results
        csv_file = 'google_places.csv'
        json_file = 'google_places.json'
        
        save_clean_csv(scraper.all_places_data, 'google_places_clean.csv')
        scraper.save_to_json(json_file)
        
        print()
        print("=" * 70)
        print("✅ SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"📊 Total places scraped: {len(scraper.all_places_data)}")
        print(f"📁 CSV file: {csv_file}")
        print(f"📁 JSON file: {json_file}")
        print()
        print("You can now open these files to view your data!")
        print("=" * 70)
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure Chrome browser is installed")
        print("2. Check your internet connection")
        print("3. Try with a different search URL")
        print("4. Reduce the number of places to scrape")
        print("=" * 70)
        
    finally:
        # Always close the browser
        print("\nClosing browser...")
        scraper.close()
        print("Done!")


if __name__ == "__main__":
    main()