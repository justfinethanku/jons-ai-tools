#!/usr/bin/env python3
"""
Test script to isolate and fix JSON parsing issues
"""

import json
import sys
import os

# Add the project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test JSON samples that are causing issues
test_responses = [
    '{ "brand_mission": "To capture authentic and timeless moments that celebrate love and life\'s milestones.", "brand_personality_traits": [ "Sophisticated", "Warm", "Approachable", "Reliable" ] }',
    
    '''```json
{ "brand_mission": "To capture authentic and timeless moments", "brand_values": ["Quality", "Authenticity"] }
```''',
    
    '{ "brand_mission": "To passionately capture authentic and timeless moments, celebrating love and life\'s milestones through artfully crafted photography that tells a unique story.", "brand_personality_traits": ["Sophisticated", "Warm", "Approachable"]}',
]

def robust_json_parse(response_text):
    """
    Robust JSON parsing with multiple fallback strategies
    """
    print(f"Testing response: {response_text[:100]}...")
    
    # Strategy 1: Direct parsing after basic cleanup
    try:
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result_data = json.loads(clean_response)
        print("✅ Strategy 1 (direct parsing) succeeded")
        return True, result_data, None
        
    except json.JSONDecodeError as e:
        print(f"❌ Strategy 1 failed: {e}")
    
    # Strategy 2: Extract content between first { and last }
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            print(f"❌ Strategy 2 failed: No valid brackets (start={start_idx}, end={end_idx})")
            return False, {}, f"No valid JSON brackets found"
            
        json_text = response_text[start_idx:end_idx+1]
        print(f"Extracted JSON: {json_text[:100]}...")
        result_data = json.loads(json_text)
        print("✅ Strategy 2 (bracket extraction) succeeded")
        return True, result_data, None
        
    except json.JSONDecodeError as e:
        print(f"❌ Strategy 2 failed: {e}")
    
    # Strategy 3: Try research_tools_framework.clean_json_response
    try:
        # Import here to avoid dependency issues in test
        from frameworks import research_tools_framework
        cleaned = research_tools_framework.clean_json_response(response_text)
        result_data = json.loads(cleaned)
        print("✅ Strategy 3 (framework cleanup) succeeded")
        return True, result_data, None
        
    except Exception as e:
        print(f"❌ Strategy 3 failed: {e}")
    
    # Final fallback: Return detailed error
    return False, {}, f"All JSON parsing strategies failed. Response: {response_text[:200]}..."

def test_analyze_brand_voice():
    """Test the actual analyze_brand_voice function"""
    try:
        from tools.brand_builder import analyze_brand_voice
        
        print("\n=== Testing analyze_brand_voice function ===")
        
        # Mock data
        client_name = "Test Photography Studio"
        website_data = {}
        form_data = {
            "industry": "Photography",
            "brand_mission": "Capture beautiful moments"
        }
        
        success, result, error = analyze_brand_voice(client_name, website_data, form_data)
        
        if success:
            print("✅ analyze_brand_voice succeeded!")
            print(f"Result keys: {list(result.keys())}")
        else:
            print(f"❌ analyze_brand_voice failed: {error}")
            
    except Exception as e:
        print(f"❌ Error testing analyze_brand_voice: {e}")

if __name__ == "__main__":
    print("=== JSON Parsing Test ===\n")
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n--- Test {i} ---")
        success, data, error = robust_json_parse(response)
        
        if success:
            print(f"✅ SUCCESS: Parsed {len(data)} keys")
        else:
            print(f"❌ FAILED: {error}")
    
    # Test the actual function that's failing
    test_analyze_brand_voice()