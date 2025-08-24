#!/usr/bin/env python3
import brotli
import json
import os
import glob

def extract_all_businesses():
    """Extract ALL business coordinates from DeyerliSen captures"""
    
    all_businesses = []
    processed_files = 0
    
    # Get all JSON capture files
    capture_files = glob.glob('captures/*.json')
    
    print(f"Processing {len(capture_files)} capture files...")
    
    for filepath in capture_files:
        filename = os.path.basename(filepath)
        
        try:
            # Decompress Brotli
            with open(filepath, 'rb') as f:
                compressed_data = f.read()
            
            decompressed_data = brotli.decompress(compressed_data)
            json_data = json.loads(decompressed_data.decode('utf-8'))
            
            processed_files += 1
            
            # Extract business data from different response formats
            businesses = []
            
            if 'data' in json_data:
                if isinstance(json_data['data'], list):
                    businesses = json_data['data']
                elif isinstance(json_data['data'], dict):
                    businesses = [json_data['data']]
            elif isinstance(json_data, list):
                businesses = json_data
            elif isinstance(json_data, dict) and 'partnerName' in json_data:
                businesses = [json_data]
            
            if businesses:
                print(f"  📋 {filename}: {len(businesses)} businesses")
                
                for business in businesses:
                    business_data = extract_business_data(business, filename)
                    if business_data:
                        all_businesses.append(business_data)
                        
        except Exception as e:
            # Skip files that can't be processed
            continue
    
    print(f"\n✅ Processed {processed_files} files successfully")
    return all_businesses

def extract_business_data(business, source_file):
    """Extract structured data for any business"""
    
    # Get all locations with coordinates
    locations = []
    if 'cities' in business:
        for city in business['cities']:
            if 'latitude' in city and 'longitude' in city:
                try:
                    locations.append({
                        'city': city.get('name', 'Unknown'),
                        'address': city.get('address', 'Unknown'),
                        'latitude': float(city['latitude']),
                        'longitude': float(city['longitude'])
                    })
                except (ValueError, TypeError):
                    continue
    
    # Only return businesses that have location data
    if not locations:
        return None
    
    return {
        'id': business.get('id'),
        'partner_id': business.get('partnerId'),
        'name': business.get('partnerName', 'Unknown'),
        'campaign_name': business.get('campaignName', ''),
        'description': business.get('description', ''),
        'category': business.get('campaignCategoryName', ''),
        'discount': business.get('discountPercent', 0),
        'rating': business.get('rating', 0),
        'locations': locations,
        'total_locations': len(locations),
        'source_file': source_file,
        'campaign_image': business.get('campaignImage', ''),
        'partner_image': business.get('partnerImage', ''),
        'expire_date': business.get('expireDate', ''),
        'start_date': business.get('startDate', ''),
        'special_offer': business.get('specialOffer', False),
        'is_new': business.get('isNew', False)
    }

def main():
    print("🏢 EXTRACTING ALL BUSINESS COORDINATES FROM DEYERLISEN")
    print("=" * 70)
    
    all_businesses = extract_all_businesses()
    
    if all_businesses:
        print(f"\n🎯 FOUND {len(all_businesses)} BUSINESSES WITH COORDINATES!")
        print("=" * 70)
        
        # Group by category
        categories = {}
        all_coordinates = []
        
        for business in all_businesses:
            category = business['category'] or 'Other'
            if category not in categories:
                categories[category] = []
            categories[category].append(business)
            
            # Add coordinates
            for location in business['locations']:
                all_coordinates.append({
                    'business_id': business['id'],
                    'partner_id': business['partner_id'],
                    'business_name': business['name'],
                    'campaign_name': business['campaign_name'],
                    'address': location['address'],
                    'city': location['city'],
                    'latitude': location['latitude'],
                    'longitude': location['longitude'],
                    'category': business['category'],
                    'rating': business['rating'],
                    'discount': business['discount'],
                    'description': business['description'][:200] + '...' if len(business['description']) > 200 else business['description']
                })
        
        # Show summary by category
        print("\n📊 BUSINESSES BY CATEGORY:")
        print("-" * 50)
        for category, businesses in sorted(categories.items()):
            coord_count = sum(len(b['locations']) for b in businesses)
            print(f"  {category}: {len(businesses)} businesses, {coord_count} locations")
        
        # Show top businesses with most locations
        print(f"\n🏢 BUSINESSES WITH MOST LOCATIONS:")
        print("-" * 50)
        top_businesses = sorted(all_businesses, key=lambda x: x['total_locations'], reverse=True)[:10]
        
        for i, business in enumerate(top_businesses, 1):
            print(f"{i:2d}. {business['name']} ({business['category']})")
            print(f"     📍 {business['total_locations']} locations, ⭐ {business['rating']}, 💰 {business['discount']}%")
            
            # Show first few locations
            for j, location in enumerate(business['locations'][:3], 1):
                lat, lon = location['latitude'], location['longitude']
                print(f"     {j}. {location['address']}")
                print(f"        📍 {lat}, {lon}")
                print(f"        🗺️ https://maps.google.com/?q={lat},{lon}")
            
            if business['total_locations'] > 3:
                print(f"     ... and {business['total_locations'] - 3} more locations")
            print()
        
        # Save all results
        results = {
            'all_businesses': all_businesses,
            'coordinates': all_coordinates,
            'categories': {cat: len(businesses) for cat, businesses in categories.items()},
            'summary': {
                'total_businesses': len(all_businesses),
                'total_coordinates': len(all_coordinates),
                'total_categories': len(categories),
                'unique_business_ids': len(set(b['id'] for b in all_businesses if b['id'])),
                'avg_locations_per_business': round(len(all_coordinates) / len(all_businesses), 2),
                'top_categories': sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            }
        }
        
        with open('deyerlisen_all_businesses.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Also save just coordinates as CSV-like format for easy use
        with open('deyerlisen_coordinates.json', 'w', encoding='utf-8') as f:
            json.dump(all_coordinates, f, ensure_ascii=False, indent=2)
        
        print(f"💾 RESULTS SAVED:")
        print(f"   📄 deyerlisen_all_businesses.json - Complete business data")
        print(f"   📍 deyerlisen_coordinates.json - Just coordinates")
        print(f"   🏢 {len(all_businesses)} businesses")
        print(f"   📍 {len(all_coordinates)} coordinate pairs")
        print(f"   📂 {len(categories)} categories")
        print(f"   🔢 {len(set(b['id'] for b in all_businesses if b['id']))} unique businesses")
        
    else:
        print("❌ No businesses with coordinates found")

if __name__ == "__main__":
    main()