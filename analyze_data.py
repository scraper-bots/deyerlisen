#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import Counter, defaultdict
import numpy as np

def load_data():
    """Load DeyerliSen business data"""
    with open('deyerlisen_all_businesses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def analyze_categories(data):
    """Analyze business categories"""
    categories = Counter()
    locations_per_category = Counter()
    
    for business in data['all_businesses']:
        category = business['category'] or 'Other'
        categories[category] += 1
        locations_per_category[category] += business['total_locations']
    
    return categories, locations_per_category

def analyze_ratings_discounts(data):
    """Analyze ratings and discounts"""
    ratings = []
    discounts = []
    categories = []
    
    for business in data['all_businesses']:
        ratings.append(business['rating'])
        discounts.append(business['discount'])
        categories.append(business['category'] or 'Other')
    
    return ratings, discounts, categories

def analyze_locations(data):
    """Analyze location distribution"""
    city_counts = Counter()
    businesses_per_location = []
    
    for business in data['all_businesses']:
        businesses_per_location.append(business['total_locations'])
        for location in business['locations']:
            city_counts[location['city']] += 1
    
    return city_counts, businesses_per_location

def create_charts(data):
    """Create comprehensive analysis charts"""
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 24))
    
    # Data analysis
    categories, locations_per_category = analyze_categories(data)
    ratings, discounts, category_list = analyze_ratings_discounts(data)
    city_counts, businesses_per_location = analyze_locations(data)
    
    # 1. Business Categories Distribution
    plt.subplot(4, 3, 1)
    top_categories = dict(categories.most_common(10))
    plt.pie(top_categories.values(), labels=top_categories.keys(), autopct='%1.1f%%', startangle=90)
    plt.title('Top 10 Business Categories Distribution', fontsize=12, fontweight='bold')
    
    # 2. Businesses per Category (Bar Chart)
    plt.subplot(4, 3, 2)
    top_cats = categories.most_common(15)
    cats, counts = zip(*top_cats)
    plt.barh(range(len(cats)), counts, color='skyblue')
    plt.yticks(range(len(cats)), cats)
    plt.xlabel('Number of Businesses')
    plt.title('Businesses per Category (Top 15)', fontsize=12, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # 3. Locations per Category
    plt.subplot(4, 3, 3)
    top_loc_cats = locations_per_category.most_common(10)
    cats, locs = zip(*top_loc_cats)
    plt.bar(range(len(cats)), locs, color='lightcoral')
    plt.xticks(range(len(cats)), cats, rotation=45, ha='right')
    plt.ylabel('Total Locations')
    plt.title('Total Locations per Category (Top 10)', fontsize=12, fontweight='bold')
    
    # 4. Rating Distribution
    plt.subplot(4, 3, 4)
    plt.hist(ratings, bins=20, color='gold', alpha=0.7, edgecolor='black')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.title('Business Ratings Distribution', fontsize=12, fontweight='bold')
    
    # 5. Discount Distribution
    plt.subplot(4, 3, 5)
    plt.hist(discounts, bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
    plt.xlabel('Discount (%)')
    plt.ylabel('Frequency')
    plt.title('Discount Percentage Distribution', fontsize=12, fontweight='bold')
    
    # 6. Rating vs Discount Scatter
    plt.subplot(4, 3, 6)
    plt.scatter(ratings, discounts, alpha=0.6, color='purple')
    plt.xlabel('Rating')
    plt.ylabel('Discount (%)')
    plt.title('Rating vs Discount Correlation', fontsize=12, fontweight='bold')
    
    # 7. Locations per Business Distribution
    plt.subplot(4, 3, 7)
    plt.hist(businesses_per_location, bins=20, color='orange', alpha=0.7, edgecolor='black')
    plt.xlabel('Number of Locations per Business')
    plt.ylabel('Frequency')
    plt.title('Locations per Business Distribution', fontsize=12, fontweight='bold')
    
    # 8. Top Cities by Business Count
    plt.subplot(4, 3, 8)
    top_cities = dict(city_counts.most_common(10))
    plt.bar(range(len(top_cities)), list(top_cities.values()), color='cyan')
    plt.xticks(range(len(top_cities)), list(top_cities.keys()), rotation=45, ha='right')
    plt.ylabel('Number of Locations')
    plt.title('Top 10 Cities by Business Locations', fontsize=12, fontweight='bold')
    
    # 9. Average Rating by Category
    plt.subplot(4, 3, 9)
    category_ratings = defaultdict(list)
    for i, cat in enumerate(category_list):
        category_ratings[cat].append(ratings[i])
    
    avg_ratings = {cat: np.mean(rats) for cat, rats in category_ratings.items()}
    top_rated_cats = dict(sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)[:10])
    
    plt.bar(range(len(top_rated_cats)), list(top_rated_cats.values()), color='pink')
    plt.xticks(range(len(top_rated_cats)), list(top_rated_cats.keys()), rotation=45, ha='right')
    plt.ylabel('Average Rating')
    plt.title('Average Rating by Category (Top 10)', fontsize=12, fontweight='bold')
    
    # 10. Average Discount by Category
    plt.subplot(4, 3, 10)
    category_discounts = defaultdict(list)
    for i, cat in enumerate(category_list):
        category_discounts[cat].append(discounts[i])
    
    avg_discounts = {cat: np.mean(discs) for cat, discs in category_discounts.items()}
    top_discount_cats = dict(sorted(avg_discounts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    plt.bar(range(len(top_discount_cats)), list(top_discount_cats.values()), color='lightblue')
    plt.xticks(range(len(top_discount_cats)), list(top_discount_cats.keys()), rotation=45, ha='right')
    plt.ylabel('Average Discount (%)')
    plt.title('Average Discount by Category (Top 10)', fontsize=12, fontweight='bold')
    
    # 11. Multi-Location vs Single-Location Businesses
    plt.subplot(4, 3, 11)
    multi_location = sum(1 for x in businesses_per_location if x > 1)
    single_location = sum(1 for x in businesses_per_location if x == 1)
    
    plt.pie([single_location, multi_location], labels=['Single Location', 'Multi-Location'], 
            autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])
    plt.title('Single vs Multi-Location Businesses', fontsize=12, fontweight='bold')
    
    # 12. Summary Statistics Box
    plt.subplot(4, 3, 12)
    plt.axis('off')
    
    stats_text = f"""
    📊 DEYERLISEN BUSINESS DATA SUMMARY
    
    🏢 Total Businesses: {len(data['all_businesses'])}
    📍 Total Locations: {sum(businesses_per_location)}
    🏗️ Unique Business IDs: {len(set(b['id'] for b in data['all_businesses'] if b['id']))}
    📂 Categories: {len(categories)}
    🏙️ Cities: {len(city_counts)}
    
    ⭐ Average Rating: {np.mean(ratings):.2f}
    💰 Average Discount: {np.mean(discounts):.1f}%
    🏢 Avg Locations/Business: {np.mean(businesses_per_location):.1f}
    
    🔝 Top Category: {categories.most_common(1)[0][0]}
    🏆 Highest Rated: {max(ratings):.1f}
    💥 Max Discount: {max(discounts):.0f}%
    """
    
    plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
             fontsize=11, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
    
    plt.tight_layout()
    plt.savefig('deyerlisen_analysis_charts.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate statistics for README
    return {
        'total_businesses': len(data['all_businesses']),
        'total_locations': sum(businesses_per_location),
        'unique_businesses': len(set(b['id'] for b in data['all_businesses'] if b['id'])),
        'categories_count': len(categories),
        'cities_count': len(city_counts),
        'avg_rating': np.mean(ratings),
        'avg_discount': np.mean(discounts),
        'avg_locations_per_business': np.mean(businesses_per_location),
        'top_category': categories.most_common(1)[0],
        'top_categories': categories.most_common(10),
        'top_cities': city_counts.most_common(10),
        'highest_rating': max(ratings),
        'max_discount': max(discounts),
        'multi_location_count': multi_location,
        'single_location_count': single_location
    }

def main():
    print("📊 Analyzing DeyerliSen Business Data...")
    
    data = load_data()
    stats = create_charts(data)
    
    print("✅ Analysis complete!")
    print(f"📊 Generated charts: deyerlisen_analysis_charts.png")
    print(f"🏢 {stats['total_businesses']} businesses analyzed")
    print(f"📍 {stats['total_locations']} locations mapped")
    print(f"📂 {stats['categories_count']} categories found")
    
    return stats

if __name__ == "__main__":
    main()