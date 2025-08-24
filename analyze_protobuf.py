#!/usr/bin/env python3
import glob
import os
from protobuf_inspector.types import StandardParser

def analyze_protobuf_files():
    """Analyze protobuf files to understand their structure"""
    pbf_files = glob.glob("captures/*.pbf")
    
    for i, pbf_file in enumerate(pbf_files[:3]):  # Analyze first 3 files
        print(f"\n=== Analyzing {pbf_file} ===")
        
        try:
            with open(pbf_file, 'rb') as f:
                data = f.read()
            
            print(f"File size: {len(data)} bytes")
            
            # Use protobuf-inspector to parse
            parser = StandardParser()
            output = parser.parse_message(data, 'Message')
            
            print("Parsed structure:")
            print(output)
            
            # Look for readable strings in the output
            output_str = str(output)
            lines = output_str.split('\n')
            
            print("\nPotential place-related strings:")
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['street', 'road', 'avenue', 'gym', 'fitness', 'sport', 'center', 'club']):
                    print(f"  {line}")
            
        except Exception as e:
            print(f"Error analyzing {pbf_file}: {e}")
            
            # Fallback: look for readable strings manually
            print("Fallback analysis - looking for readable text:")
            try:
                text_candidates = []
                for i in range(len(data) - 3):
                    # Look for sequences that might be text
                    if data[i] > 0 and data[i] < 200:  # potential string length
                        length = data[i]
                        if i + 1 + length < len(data):
                            try:
                                candidate = data[i+1:i+1+length].decode('utf-8')
                                if (len(candidate) > 3 and 
                                    candidate.isprintable() and 
                                    any(c.isalpha() for c in candidate) and
                                    not candidate.startswith('http')):
                                    text_candidates.append(candidate)
                            except UnicodeDecodeError:
                                pass
                
                if text_candidates:
                    print("Found potential text strings:")
                    for candidate in text_candidates[:10]:
                        print(f"  '{candidate}'")
                else:
                    print("No readable text found")
                    
            except Exception as fallback_e:
                print(f"Fallback analysis also failed: {fallback_e}")

if __name__ == "__main__":
    analyze_protobuf_files()