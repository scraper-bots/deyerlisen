#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import Counter, defaultdict
import numpy as np
import os

def load_data():
    """Load DeyerliSen business data"""
    with open('deyerlisen_all_businesses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_individual_charts(data):
    """Create separate individual charts for better understanding"""
    
    # Create charts directory
    os.makedirs('charts', exist_ok=True)
    
    plt.style.use('seaborn-v0_8')
    
    # Data preparation
    categories = Counter()
    locations_per_category = Counter()
    ratings = []
    discounts = []
    category_list = []
    city_counts = Counter()
    businesses_per_location = []
    
    for business in data['all_businesses']:
        category = business['category'] or 'Other'
        categories[category] += 1
        locations_per_category[category] += business['total_locations']
        ratings.append(business['rating'])
        discounts.append(business['discount'])
        category_list.append(category)
        businesses_per_location.append(business['total_locations'])
        
        for location in business['locations']:
            city_counts[location['city']] += 1
    
    # 1. Business Categories Pie Chart
    plt.figure(figsize=(12, 8))
    top_categories = dict(categories.most_common(10))
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_categories)))
    plt.pie(top_categories.values(), labels=top_categories.keys(), autopct='%1.1f%%', 
            startangle=90, colors=colors)
    plt.title('Business Categories Distribution (Top 10)', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('charts/01_categories_pie.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Businesses per Category Bar Chart
    plt.figure(figsize=(14, 8))
    top_cats = categories.most_common(15)
    cats, counts = zip(*top_cats)
    colors = plt.cm.viridis(np.linspace(0, 1, len(cats)))
    plt.barh(range(len(cats)), counts, color=colors)
    plt.yticks(range(len(cats)), cats)
    plt.xlabel('Number of Businesses', fontsize=12)
    plt.title('Number of Businesses per Category (Top 15)', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()
    for i, v in enumerate(counts):
        plt.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/02_businesses_per_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Total Locations per Category
    plt.figure(figsize=(12, 8))
    top_loc_cats = locations_per_category.most_common(10)
    cats, locs = zip(*top_loc_cats)
    colors = plt.cm.plasma(np.linspace(0, 1, len(cats)))
    bars = plt.bar(range(len(cats)), locs, color=colors)
    plt.xticks(range(len(cats)), cats, rotation=45, ha='right')
    plt.ylabel('Total Locations', fontsize=12)
    plt.title('Total Locations per Category (Top 10)', fontsize=16, fontweight='bold', pad=20)
    for i, v in enumerate(locs):
        plt.text(i, v + 2, str(v), ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/03_locations_per_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Rating Distribution Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(ratings, bins=20, color='gold', alpha=0.8, edgecolor='black', linewidth=1.2)
    plt.xlabel('Rating', fontsize=12)
    plt.ylabel('Number of Businesses', fontsize=12)
    plt.title('Business Ratings Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.axvline(np.mean(ratings), color='red', linestyle='--', linewidth=2, 
                label=f'Average: {np.mean(ratings):.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/04_rating_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Discount Distribution Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(discounts, bins=20, color='lightgreen', alpha=0.8, edgecolor='black', linewidth=1.2)
    plt.xlabel('Discount Percentage (%)', fontsize=12)
    plt.ylabel('Number of Businesses', fontsize=12)
    plt.title('Discount Percentage Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.axvline(np.mean(discounts), color='red', linestyle='--', linewidth=2, 
                label=f'Average: {np.mean(discounts):.1f}%')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/05_discount_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Rating vs Discount Scatter Plot
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(ratings, discounts, alpha=0.7, c=discounts, cmap='viridis', s=60)
    plt.xlabel('Rating', fontsize=12)
    plt.ylabel('Discount Percentage (%)', fontsize=12)
    plt.title('Rating vs Discount Correlation', fontsize=16, fontweight='bold', pad=20)
    plt.colorbar(scatter, label='Discount %')
    
    # Add correlation coefficient
    correlation = np.corrcoef(ratings, discounts)[0,1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=plt.gca().transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/06_rating_vs_discount.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. Locations per Business Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(businesses_per_location, bins=range(1, max(businesses_per_location)+2), 
             color='orange', alpha=0.8, edgecolor='black', linewidth=1.2)
    plt.xlabel('Number of Locations per Business', fontsize=12)
    plt.ylabel('Number of Businesses', fontsize=12)
    plt.title('Locations per Business Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.axvline(np.mean(businesses_per_location), color='red', linestyle='--', linewidth=2, 
                label=f'Average: {np.mean(businesses_per_location):.1f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/07_locations_per_business.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 8. Top Cities by Business Count
    plt.figure(figsize=(12, 8))
    top_cities = dict(city_counts.most_common(10))
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_cities)))
    bars = plt.bar(range(len(top_cities)), list(top_cities.values()), color=colors)
    plt.xticks(range(len(top_cities)), list(top_cities.keys()), rotation=45, ha='right')
    plt.ylabel('Number of Business Locations', fontsize=12)
    plt.title('Top 10 Cities by Business Locations', fontsize=16, fontweight='bold', pad=20)
    for i, v in enumerate(top_cities.values()):
        plt.text(i, v + 1, str(v), ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/08_top_cities.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 9. Average Rating by Category
    plt.figure(figsize=(14, 8))
    category_ratings = defaultdict(list)
    for i, cat in enumerate(category_list):
        category_ratings[cat].append(ratings[i])
    
    avg_ratings = {cat: np.mean(rats) for cat, rats in category_ratings.items()}
    top_rated_cats = dict(sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)[:12])
    
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(top_rated_cats)))
    bars = plt.bar(range(len(top_rated_cats)), list(top_rated_cats.values()), color=colors)
    plt.xticks(range(len(top_rated_cats)), list(top_rated_cats.keys()), rotation=45, ha='right')
    plt.ylabel('Average Rating', fontsize=12)
    plt.title('Average Rating by Category (Top 12)', fontsize=16, fontweight='bold', pad=20)
    plt.ylim(0, 5)
    for i, v in enumerate(top_rated_cats.values()):
        plt.text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/09_avg_rating_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 10. Average Discount by Category
    plt.figure(figsize=(14, 8))
    category_discounts = defaultdict(list)
    for i, cat in enumerate(category_list):
        category_discounts[cat].append(discounts[i])
    
    avg_discounts = {cat: np.mean(discs) for cat, discs in category_discounts.items()}
    top_discount_cats = dict(sorted(avg_discounts.items(), key=lambda x: x[1], reverse=True)[:12])
    
    colors = plt.cm.Reds(np.linspace(0.3, 1, len(top_discount_cats)))
    bars = plt.bar(range(len(top_discount_cats)), list(top_discount_cats.values()), color=colors)
    plt.xticks(range(len(top_discount_cats)), list(top_discount_cats.keys()), rotation=45, ha='right')
    plt.ylabel('Average Discount (%)', fontsize=12)
    plt.title('Average Discount by Category (Top 12)', fontsize=16, fontweight='bold', pad=20)
    for i, v in enumerate(top_discount_cats.values()):
        plt.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/10_avg_discount_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 11. Single vs Multi-Location Businesses
    plt.figure(figsize=(8, 8))
    multi_location = sum(1 for x in businesses_per_location if x > 1)
    single_location = sum(1 for x in businesses_per_location if x == 1)
    
    sizes = [single_location, multi_location]
    labels = [f'Single Location\n({single_location} businesses)', 
              f'Multi-Location\n({multi_location} businesses)']
    colors = ['#ff9999', '#66b3ff']
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90,
            textprops={'fontsize': 12})
    plt.title('Single vs Multi-Location Businesses', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('charts/11_single_vs_multi_location.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 12. Business Density Heatmap by Category vs Rating Range
    plt.figure(figsize=(12, 8))
    
    # Create rating ranges
    rating_ranges = ['0-2', '2-3', '3-4', '4-4.5', '4.5-5']
    top_categories_list = [cat for cat, _ in categories.most_common(10)]
    
    # Create matrix
    heatmap_data = np.zeros((len(top_categories_list), len(rating_ranges)))
    
    for i, business in enumerate(data['all_businesses']):
        cat = business['category'] or 'Other'
        if cat in top_categories_list:
            rating = business['rating']
            cat_idx = top_categories_list.index(cat)
            
            if rating < 2:
                rating_idx = 0
            elif rating < 3:
                rating_idx = 1
            elif rating < 4:
                rating_idx = 2
            elif rating < 4.5:
                rating_idx = 3
            else:
                rating_idx = 4
            
            heatmap_data[cat_idx][rating_idx] += 1
    
    sns.heatmap(heatmap_data, 
                xticklabels=rating_ranges,
                yticklabels=top_categories_list,
                annot=True, 
                fmt='g', 
                cmap='YlOrRd',
                cbar_kws={'label': 'Number of Businesses'})
    
    plt.title('Business Distribution: Category vs Rating Range', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Rating Range', fontsize=12)
    plt.ylabel('Category', fontsize=12)
    plt.tight_layout()
    plt.savefig('charts/12_category_rating_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Individual charts created successfully!")
    print("📁 Charts saved in 'charts/' directory:")
    for i in range(1, 13):
        print(f"   📊 {i:02d}_*.png")

def main():
    print("📊 Creating Individual Charts for Better Understanding...")
    
    data = load_data()
    create_individual_charts(data)
    
    print("\n🎯 All individual charts generated!")
    print("📁 Check the 'charts/' directory for detailed visualizations")

if __name__ == "__main__":
    main()