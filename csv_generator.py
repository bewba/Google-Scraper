import csv
import re

def clean_text(text):
    """Remove weird symbols, extra whitespace, and newlines."""
    if not text:
        return ""
    # Remove non-standard unicode characters (like , , etc.)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def save_clean_csv(places, filename='google_places_clean.csv'):
    """
    Save Google Maps scraped data to a cleaned CSV, sorted by name.
    """
    # Define the columns we want
    headers = [
        'Name', 'Address', 'Category', 'Rating', 'Reviews',
        'Phone', 'Website', 'Google Maps URL'
    ]
    
    # Clean and normalize data
    cleaned_places = []
    for place in places:
        cleaned_place = {
            'Name': clean_text(place.get('name')),
            'Address': clean_text(place.get('address')),
            'Category': clean_text(place.get('category')),
            'Rating': place.get('rating', ''),
            'Reviews': place.get('review_count', '').replace('(', '').replace(')', ''),
            'Phone': clean_text(place.get('phone')),
            'Website': place.get('website', ''),
            'Google Maps URL': place.get('url', '')
        }
        cleaned_places.append(cleaned_place)
    
    # Sort alphabetically by Name
    cleaned_places.sort(key=lambda x: x['Name'].lower())
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in cleaned_places:
            writer.writerow(row)
    
    print(f"✅ Clean CSV saved as {filename} ({len(cleaned_places)} places)")

# Usage:
# save_clean_csv(scraper.all_places_data)
