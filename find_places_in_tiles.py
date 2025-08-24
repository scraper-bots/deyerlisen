#!/usr/bin/env python3
import json
import glob
import os
import re

def analyze_extracted_data():
    """Look for patterns that might indicate place data"""
    
    with open('google_maps_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total files analyzed: {len(data)}")
    
    # Group by file to find the richest data sources
    file_stats = {}
    all_strings = []
    coordinates = []
    
    for file_data in data:
        source_file = file_data['source_file']
        items = file_data['items']
        
        if source_file not in file_stats:
            file_stats[source_file] = {
                'total_items': 0,
                'strings': [],
                'coords': [],
                'file_size': file_data.get('file_size', 0)
            }
        
        for item in items:
            file_stats[source_file]['total_items'] += 1
            
            if 'name' in item:
                string_val = item['name']
                file_stats[source_file]['strings'].append(string_val)
                all_strings.append(string_val)
                
            elif 'coordinate' in item:
                coord_val = item['coordinate']
                file_stats[source_file]['coords'].append(coord_val)
                coordinates.append(coord_val)
    
    # Find files with most potential place data
    rich_files = sorted(file_stats.items(), key=lambda x: x[1]['total_items'], reverse=True)
    
    print(f"\nTop 10 files with most extracted items:")
    for file_path, stats in rich_files[:10]:
        print(f"  {file_path}: {stats['total_items']} items ({stats['file_size']} bytes)")
        if stats['strings']:
            interesting_strings = [s for s in stats['strings'] 
                                 if not s.startswith('application/') 
                                 and not s.startswith('E') 
                                 and len(s) > 5][:3]
            if interesting_strings:
                print(f"    Sample strings: {interesting_strings}")
    
    # Look for patterns in coordinates
    realistic_coords = [c for c in coordinates if -180 <= c <= 180 and abs(c) > 0.001]
    if realistic_coords:
        print(f"\nFound {len(realistic_coords)} potentially realistic coordinates:")
        print(f"  Lat/Lon range: {min(realistic_coords):.6f} to {max(realistic_coords):.6f}")
        
        # Group coordinates that might be lat/lon pairs
        lat_range = [c for c in realistic_coords if -90 <= c <= 90]
        lon_range = [c for c in realistic_coords if -180 <= c <= 180]
        
        print(f"  Potential latitudes: {len(lat_range)}")
        print(f"  Potential longitudes: {len(lon_range)}")
        
        if lat_range and lon_range:
            print(f"  Sample coordinates: {lat_range[:5]}, {lon_range[:5]}")
    
    # Look for non-encoded strings
    interesting_strings = []
    for s in all_strings:
        if (not s.startswith('application/') and 
            not s.startswith('E') and 
            len(s) > 3 and len(s) < 50 and
            any(c.isalpha() for c in s) and
            not re.match(r'^[A-Za-z0-9+/=]+$', s)):  # not base64-like
            interesting_strings.append(s)
    
    if interesting_strings:
        print(f"\nFound {len(interesting_strings)} potentially interesting strings:")
        unique_strings = list(set(interesting_strings))[:10]
        for s in unique_strings:
            print(f"  '{s}'")
    else:
        print(f"\nNo obviously readable place names found in extracted data")
    
    # Check if we should look at specific large files
    if rich_files:
        largest_file = rich_files[0][0]
        print(f"\nAnalyzing largest data file: {largest_file}")
        
        # Read the raw binary to look for other patterns
        try:
            with open(largest_file, 'rb') as f:
                raw_data = f.read()
            
            # Look for UTF-8 text sequences
            text_sequences = []
            i = 0
            while i < len(raw_data) - 10:
                try:
                    # Try to decode sequences
                    for length in [3, 5, 10, 20]:
                        if i + length < len(raw_data):
                            try:
                                text = raw_data[i:i+length].decode('utf-8')
                                if (text.isprintable() and 
                                    any(c.isalpha() for c in text) and 
                                    len(text.strip()) > 2):
                                    text_sequences.append(text.strip())
                            except UnicodeDecodeError:
                                pass
                    i += 1
                except:
                    i += 1
            
            if text_sequences:
                unique_sequences = list(set(text_sequences))[:10]
                print(f"  Found {len(unique_sequences)} text sequences in raw data:")
                for seq in unique_sequences:
                    if len(seq) > 3:
                        print(f"    '{seq}'")
        except Exception as e:
            print(f"  Error reading raw data: {e}")

if __name__ == "__main__":
    analyze_extracted_data()