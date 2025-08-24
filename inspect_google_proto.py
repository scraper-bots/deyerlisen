#!/usr/bin/env python3
import os
import glob
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
import json

def inspect_protobuf_raw(data):
    """Try to parse protobuf without knowing the schema"""
    # This is a basic inspection - Google Maps uses custom protobuf schemas
    print(f"Raw protobuf size: {len(data)} bytes")
    print(f"First 100 bytes (hex): {data[:100].hex()}")
    
    # Look for text patterns that might be place names
    try:
        text_parts = []
        i = 0
        while i < len(data) - 1:
            # Look for length-prefixed strings (common in protobuf)
            if data[i] > 0 and data[i] < 100:  # reasonable string length
                length = data[i]
                if i + 1 + length < len(data):
                    try:
                        text = data[i+1:i+1+length].decode('utf-8')
                        if len(text) > 2 and text.isprintable() and ' ' in text:
                            text_parts.append(text)
                    except UnicodeDecodeError:
                        pass
            i += 1
        
        if text_parts:
            print("\nPossible text strings found:")
            for text in text_parts[:20]:  # Show first 20
                print(f"  '{text}'")
        else:
            print("\nNo obvious text strings found")
            
    except Exception as e:
        print(f"Error inspecting: {e}")

def main():
    pbf_files = glob.glob("captures/*.pbf")
    for pbf_file in pbf_files[:3]:  # Just check first 3 files
        print(f"\n=== Inspecting {pbf_file} ===")
        with open(pbf_file, 'rb') as f:
            data = f.read()
        inspect_protobuf_raw(data)

if __name__ == "__main__":
    main()