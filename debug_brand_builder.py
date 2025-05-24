#!/usr/bin/env python3
"""
Debug script to test Brand Builder UI workflow step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_comprehensive_client_analysis():
    """Test the comprehensive_client_analysis function that might be causing issues"""
    try:
        from tools.brand_builder import comprehensive_client_analysis
        
        print("=== Testing comprehensive_client_analysis ===")
        
        # Mock form data
        form_data = {
            "industry": "Photography",
            "product_service_description": "Wedding and portrait photography",
            "brand_mission": "Capture beautiful moments"
        }
        
        # Test without website (should work)
        print("\n--- Test 1: No Website ---")
        success, result, error = comprehensive_client_analysis(
            client_name="Test Studio",
            industry="Photography", 
            website_url=None,
            form_data=form_data,
            optimize_content=True
        )
        
        if success:
            print("✅ No website test succeeded!")
            print(f"Result keys: {list(result.keys())}")
        else:
            print(f"❌ No website test failed: {error}")
        
        # Test with invalid website (should handle gracefully)
        print("\n--- Test 2: Invalid Website ---")
        success, result, error = comprehensive_client_analysis(
            client_name="Test Studio",
            industry="Photography",
            website_url="https://nonexistent-website-12345.com",
            form_data=form_data,
            optimize_content=True
        )
        
        if success:
            print("✅ Invalid website test succeeded!")
        else:
            print(f"❌ Invalid website test failed: {error}")
            
    except Exception as e:
        print(f"❌ Error in comprehensive_client_analysis test: {e}")

def test_form_submission_path():
    """Test the form submission code path that users hit"""
    try:
        print("\n=== Testing Form Submission Path ===")
        
        # This mimics what happens when user clicks "Enhance with AI"
        from tools.brand_builder import analyze_brand_voice
        
        # Mock current form data (from UI form)
        current_form_data = {
            "industry": "Photography",
            "product_service_description": "Wedding photography services",
            "current_target_audience": "Engaged couples",
            "ideal_target_audience": "Luxury wedding clients",
            "brand_values": "Quality, Authenticity, Elegance",
            "brand_mission": "To capture the most important day of your life",
            "desired_emotional_impact": "Joy, Nostalgia, Love",
            "brand_personality": "Professional, Warm, Creative",
            "words_tones_to_avoid": "Cheap, Fast, Basic"
        }
        
        success, analysis_result, error_msg = analyze_brand_voice(
            "Test Photography Studio",
            {},  # Empty website_data since we're using rich form_data
            current_form_data
        )
        
        if success:
            print("✅ Form submission path test succeeded!")
            print(f"Analysis result has {len(analysis_result)} fields")
            
            # Check if we have the key fields
            required_fields = ['brand_mission', 'brand_values', 'current_target_audience']
            missing_fields = [field for field in required_fields if field not in analysis_result]
            
            if missing_fields:
                print(f"⚠️  Missing expected fields: {missing_fields}")
            else:
                print("✅ All expected fields present")
                
        else:
            print(f"❌ Form submission path failed: {error_msg}")
            
    except Exception as e:
        print(f"❌ Error in form submission test: {e}")
        import traceback
        traceback.print_exc()

def test_notion_data_mapping():
    """Test the Notion data mapping that might be causing issues"""
    try:
        print("\n=== Testing Notion Data Mapping ===")
        
        # Mock analysis result
        analysis_result = {
            "brand_mission": "To capture beautiful moments",
            "brand_values": ["Quality", "Authenticity"],
            "brand_personality_traits": ["Professional", "Warm"],
            "current_target_audience": "Engaged couples",
            "ideal_target_audience": "Luxury clients",
            "desired_emotional_impact": ["Joy", "Love"],
            "words_tones_to_avoid": ["Cheap", "Fast"]
        }
        
        # This is the mapping logic from the UI
        notion_data = {
            "Website": "https://example.com",
            "Industry": analysis_result.get("industry", "Photography"),
            "Product_Service_Description": analysis_result.get("company_description", analysis_result.get("product_service_description", "")),
            "Current_Target_Audience": analysis_result.get("current_target_audience", ""),
            "Ideal_Target_Audience": analysis_result.get("ideal_target_audience", ""),
            "Brand_Values": ', '.join(analysis_result.get("brand_values", [])) if isinstance(analysis_result.get("brand_values"), list) else analysis_result.get("brand_values", ""),
            "Brand_Mission": analysis_result.get("brand_mission", ""),
            "Desired_Emotional_Impact": ', '.join(analysis_result.get("desired_emotional_impact", [])) if isinstance(analysis_result.get("desired_emotional_impact"), list) else analysis_result.get("desired_emotional_impact", ""),
            "Brand_Personality": ', '.join(analysis_result.get("brand_personality_traits", [])) if isinstance(analysis_result.get("brand_personality_traits"), list) else analysis_result.get("brand_personality", ""),
            "Words_Tones_To_Avoid": ', '.join(analysis_result.get("words_tones_to_avoid", [])) if isinstance(analysis_result.get("words_tones_to_avoid"), list) else analysis_result.get("words_tones_to_avoid", ""),
        }
        
        print("✅ Notion data mapping test succeeded!")
        print("Mapped fields:")
        for key, value in notion_data.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error in Notion mapping test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_client_analysis()
    test_form_submission_path()
    test_notion_data_mapping()
    
    print("\n=== Summary ===")
    print("If all tests passed, the issue might be:")
    print("1. Frontend UI state management")
    print("2. Streamlit session state conflicts") 
    print("3. Database connection issues")
    print("4. Missing environment variables")
    print("5. Import/dependency issues in the Streamlit environment")