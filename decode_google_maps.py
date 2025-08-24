#!/usr/bin/env python3
import os
import glob
import json
import struct
from typing import List, Dict, Any

def read_varint(data, offset):
    """Read a varint from protobuf data"""
    result = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            break
        shift += 7
        if shift >= 64:
            raise ValueError("Varint too long")
    return result, offset

def read_string(data, offset, length):
    """Read a string of given length"""
    if offset + length > len(data):
        return None, offset
    try:
        return data[offset:offset + length].decode('utf-8'), offset + length
    except UnicodeDecodeError:
        return None, offset + length

def parse_protobuf_field(data, offset):
    """Parse a single protobuf field"""
    if offset >= len(data):
        return None, offset
    
    try:
        tag_and_type, offset = read_varint(data, offset)
        field_num = tag_and_type >> 3
        wire_type = tag_and_type & 0x7
        
        if wire_type == 0:  # Varint
            value, offset = read_varint(data, offset)
            return {'field': field_num, 'type': 'varint', 'value': value}, offset
        elif wire_type == 1:  # 64-bit
            if offset + 8 > len(data):
                return None, offset + 8
            value = struct.unpack('<d', data[offset:offset+8])[0]
            return {'field': field_num, 'type': 'double', 'value': value}, offset + 8
        elif wire_type == 2:  # Length-delimited (string/bytes/embedded message)
            length, offset = read_varint(data, offset)
            if offset + length > len(data):
                return None, offset + length
            
            # Try to decode as string first
            string_val, _ = read_string(data, offset, length)
            if string_val and string_val.isprintable():
                return {'field': field_num, 'type': 'string', 'value': string_val}, offset + length
            else:
                # Could be embedded message or binary data
                raw_data = data[offset:offset + length]
                return {'field': field_num, 'type': 'bytes', 'value': raw_data, 'length': length}, offset + length
        elif wire_type == 5:  # 32-bit
            if offset + 4 > len(data):
                return None, offset + 4
            value = struct.unpack('<f', data[offset:offset+4])[0]
            return {'field': field_num, 'type': 'float', 'value': value}, offset + 4
        else:
            return None, offset
            
    except Exception:
        return None, offset + 1

def extract_places_from_protobuf(data):
    """Extract potential place data from Google Maps protobuf"""
    places = []
    offset = 0
    
    while offset < len(data):
        field, offset = parse_protobuf_field(data, offset)
        if field is None:
            offset += 1
            continue
            
        # Look for string fields that might be place names
        if field['type'] == 'string':
            value = field['value']
            # Filter for potential place names (more than 2 chars, contains letters)
            if len(value) > 2 and any(c.isalpha() for c in value):
                places.append({
                    'name': value,
                    'field_number': field['field'],
                    'type': 'string'
                })
        
        # Look for coordinate-like doubles
        elif field['type'] in ['double', 'float']:
            value = field['value']
            # Check if it looks like a coordinate (lat/lon range)
            if -180 <= value <= 180:
                places.append({
                    'coordinate': value,
                    'field_number': field['field'],
                    'type': field['type']
                })
        
        # Look for embedded messages that might contain place data
        elif field['type'] == 'bytes' and field['length'] > 10:
            nested_places = extract_places_from_protobuf(field['value'])
            for place in nested_places:
                place['parent_field'] = field['field']
                places.append(place)
    
    return places

def process_captured_files():
    """Process all captured protobuf files"""
    pbf_files = glob.glob("captures/*.pbf")
    all_data = []
    
    for pbf_file in pbf_files:
        print(f"Processing {pbf_file}...")
        
        try:
            with open(pbf_file, 'rb') as f:
                data = f.read()
            
            places = extract_places_from_protobuf(data)
            
            if places:
                print(f"  Found {len(places)} potential items")
                file_data = {
                    'source_file': pbf_file,
                    'file_size': len(data),
                    'items': places
                }
                all_data.append(file_data)
            else:
                print(f"  No items found")
                
        except Exception as e:
            print(f"  Error processing {pbf_file}: {e}")
    
    # Save results
    output_file = "google_maps_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {output_file}")
    
    # Show summary
    total_places = sum(len(file_data['items']) for file_data in all_data)
    print(f"Total items extracted: {total_places}")
    
    # Show sample data
    if total_places > 0:
        print("\nSample extracted data:")
        for file_data in all_data[:2]:  # Show first 2 files
            print(f"\nFrom {file_data['source_file']}:")
            for item in file_data['items'][:5]:  # Show first 5 items
                if 'name' in item:
                    print(f"  Name: '{item['name']}' (field {item['field_number']})")
                elif 'coordinate' in item:
                    print(f"  Coordinate: {item['coordinate']} (field {item['field_number']})")

if __name__ == "__main__":
    process_captured_files()