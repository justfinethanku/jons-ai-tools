#!/usr/bin/env python3
"""
Debug Step 2 JSON parsing issue
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.brand_builder.step_02_brand_analyzer import robust_json_parse


def test_json_parsing_with_sample():
    """Test with the actual response format we're getting"""
    
    # Sample response that looks like what we're getting
    sample_response = '''{ 
    "brand_mission": "To capture authentic and timeless moments that celebrate love and life's milestones.",
    "brand_personality_traits": [
        "Sophisticated",
        "Warm", 
        "Approachable",
        "Reliable",
        "Creative"
    ],
    "current_target_audience": "Engaged couples planning their wedding",
    "ideal_target_audience": "Luxury wedding clients who value artistry and professionalism",
    "brand_values": ["Quality", "Authenticity", "Excellence", "Creativity"],
    "value_proposition": "Creating beautiful, timeless photography that captures your most precious moments",
    "communication_tone": "Professional yet warm and approachable",
    "voice_characteristics": ["Elegant", "Reassuring", "Knowledgeable"],
    "language_level": "Professional but accessible",
    "desired_emotional_impact": ["Joy", "Confidence", "Excitement"],
    "brand_archetypes": ["Creator", "Caregiver"],
    "competitive_differentiation": "Focus on artistic storytelling and emotional connection",
    "content_themes": ["Love stories", "Milestone celebrations", "Artistic vision"],
    "words_tones_to_avoid": ["Cheap", "Fast", "Basic", "Generic"],
    "messaging_priorities": ["Quality craftsmanship", "Emotional connection", "Professional service"]
}'''
    
    print("🧪 Testing JSON parsing with sample response...")
    print(f"📏 Response length: {len(sample_response)} characters")
    print(f"📋 Response preview: {sample_response[:100]}...")
    
    # Test our robust parsing
    success, data, error = robust_json_parse(sample_response)
    
    if success:
        print("✅ JSON parsing successful!")
        print(f"📊 Parsed {len(data)} fields:")
        for key in list(data.keys())[:5]:  # Show first 5 keys
            print(f"  - {key}: {str(data[key])[:50]}...")
        return True
    else:
        print("❌ JSON parsing failed!")
        print(f"🔍 Error: {error}")
        
        # Try basic json.loads
        print("\n🔧 Testing basic json.loads...")
        try:
            basic_result = json.loads(sample_response)
            print("✅ Basic json.loads works fine!")
            print(f"📊 Basic parsing got {len(basic_result)} fields")
            return False  # Our parser is broken if basic works
        except json.JSONDecodeError as e:
            print(f"❌ Basic json.loads also failed: {e}")
            return False


def test_json_parsing_edge_cases():
    """Test edge cases that might be causing issues"""
    
    print("\n🔍 Testing edge cases...")
    
    # Test 1: JSON with extra whitespace
    test1 = '''  
    { "test": "value" }  
    '''
    
    success1, data1, error1 = robust_json_parse(test1)
    print(f"Test 1 (whitespace): {'✅' if success1 else '❌'} - {error1 if not success1 else 'OK'}")
    
    # Test 2: JSON with newlines
    test2 = '''{ 
    "test": "value",
    "array": ["item1", "item2"]
}'''
    
    success2, data2, error2 = robust_json_parse(test2)
    print(f"Test 2 (newlines): {'✅' if success2 else '❌'} - {error2 if not success2 else 'OK'}")
    
    # Test 3: JSON with text before/after
    test3 = '''Here's your JSON response:
{ "test": "value" }
End of response.'''
    
    success3, data3, error3 = robust_json_parse(test3)
    print(f"Test 3 (extra text): {'✅' if success3 else '❌'} - {error3 if not success3 else 'OK'}")
    
    return success1 and success2 and success3


def debug_actual_api_response():
    """Try to get an actual API response to debug"""
    print("\n🚀 Testing with actual API call...")
    
    try:
        from tools.brand_builder.step_02_brand_analyzer import BrandAnalyzerTool
        from tools.brand_builder import WorkflowContext
        
        # Create minimal context
        context = WorkflowContext({
            'client_name': 'Test Photography Studio',
            'brand_mission': 'Capture beautiful moments'
        })
        
        step = BrandAnalyzerTool()
        result = step.execute(context)
        
        if result.success:
            print("✅ Actual API call successful!")
            print(f"📊 Got {len(result.data)} fields")
            return True
        else:
            print("❌ Actual API call failed!")
            for error in result.errors:
                print(f"🔍 Error: {error}")
            return False
            
    except Exception as e:
        print(f"❌ API test crashed: {e}")
        return False


def main():
    """Run all debugging tests"""
    print("🧪 Debugging Step 2 JSON Parsing Issue")
    print("=" * 50)
    
    tests = [
        ("Sample Response Parsing", test_json_parsing_with_sample),
        ("Edge Cases", test_json_parsing_edge_cases),
        ("Actual API Response", debug_actual_api_response)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG RESULTS:")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    print(f"\n🏆 {passed}/{len(results)} tests passed")
    
    if passed < len(results):
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check if JSON response is being truncated")
        print("2. Verify robust_json_parse logic")
        print("3. Test with complete response data")


if __name__ == "__main__":
    main()