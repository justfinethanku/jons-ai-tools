#!/usr/bin/env python3
"""
Test backward compatibility of the updated brand_builder.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_legacy_functions():
    """Test that the original functions still work"""
    print("🔄 Testing backward compatibility...")
    
    # Import directly from the brand_builder.py file  
    from tools.brand_builder import extract_website_data, analyze_brand_voice
    
    # Test extract_website_data
    print("📄 Testing extract_website_data...")
    success, data, error = extract_website_data("Test Company", "https://anthropic.com")
    
    if success:
        print("✅ extract_website_data works!")
        print(f"📊 Extracted {len(data)} fields")
    else:
        print(f"❌ extract_website_data failed: {error}")
        return False
    
    # Test analyze_brand_voice  
    print("🎯 Testing analyze_brand_voice...")
    success2, data2, error2 = analyze_brand_voice("Test Company", data)
    
    if success2:
        print("✅ analyze_brand_voice works!")
        print(f"📊 Generated {len(data2)} insights")
    else:
        print(f"❌ analyze_brand_voice failed: {error2}")
        return False
    
    return True


def test_comprehensive_analysis():
    """Test comprehensive_client_analysis function"""
    print("\n🚀 Testing comprehensive_client_analysis...")
    
    from tools.brand_builder import comprehensive_client_analysis
    
    success, data, error = comprehensive_client_analysis(
        "Test Company",
        "Technology", 
        "https://anthropic.com",
        {"brand_mission": "Test mission"}
    )
    
    if success:
        print("✅ comprehensive_client_analysis works!")
        print(f"📊 Generated {len(data)} fields")
        return True
    else:
        print(f"❌ comprehensive_client_analysis failed: {error}")
        return False


def main():
    """Test backward compatibility"""
    print("🧪 Testing Brand Builder Backward Compatibility")
    print("=" * 50)
    
    tests = [
        ("Legacy Functions", test_legacy_functions),
        ("Comprehensive Analysis", test_comprehensive_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 COMPATIBILITY TEST RESULTS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🏆 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Perfect backward compatibility! Existing code will work unchanged.")
    else:
        print("⚠️  Some compatibility issues found.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)