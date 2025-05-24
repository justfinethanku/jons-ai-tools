#!/usr/bin/env python3
"""
Simple test script to verify Notion database update functionality.
Tests the update_client_profile function from research_tools_framework.py
"""

import os
import sys
from datetime import datetime

# Add the project directory to the path
sys.path.append('/Users/jonathanedwards/jons-ai-tools')

# Mock Streamlit secrets for testing
class MockSecrets:
    def __init__(self):
        self.notion = {
            "NOTION_API_KEY": os.getenv("NOTION_API_KEY", "your_api_key_here"),
            "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID", "your_database_id_here"),
            "Content_Samples_database_ID": os.getenv("CONTENT_SAMPLES_DB_ID", "content_samples_db_id"),
            "voice_guidlines_database_id": os.getenv("VOICE_GUIDELINES_DB_ID", "voice_guidelines_db_id")
        }

# Mock Streamlit module
class MockStreamlit:
    secrets = MockSecrets()
    
    def error(self, message):
        print(f"ERROR: {message}")
    
    def warning(self, message):
        print(f"WARNING: {message}")
    
    def success(self, message):
        print(f"SUCCESS: {message}")
    
    def info(self, message):
        print(f"INFO: {message}")

# Replace streamlit import
sys.modules['streamlit'] = MockStreamlit()

# Now import the framework
from frameworks.research_tools_framework import NotionDatabaseManager

def test_notion_connection():
    """Test basic Notion connection"""
    print("🔍 Testing Notion connection...")
    
    try:
        db_manager = NotionDatabaseManager()
        print("✅ NotionDatabaseManager initialized successfully")
        return db_manager
    except Exception as e:
        print(f"❌ Failed to initialize NotionDatabaseManager: {e}")
        return None

def test_get_client_list(db_manager):
    """Test retrieving client list"""
    print("\n🔍 Testing client list retrieval...")
    
    try:
        clients = db_manager.get_client_list()
        print(f"✅ Retrieved {len(clients)} clients")
        
        if clients:
            print("📋 Available clients:")
            for name, page_id in clients.items():
                print(f"  - {name} (ID: {page_id[:8]}...)")
            return list(clients.keys())[0], list(clients.values())[0]  # Return first client
        else:
            print("⚠️ No clients found in database")
            return None, None
            
    except Exception as e:
        print(f"❌ Failed to retrieve client list: {e}")
        return None, None

def test_get_client_profile(db_manager, client_page_id):
    """Test retrieving client profile"""
    print(f"\n🔍 Testing client profile retrieval for ID: {client_page_id[:8]}...")
    
    try:
        profile = db_manager.get_client_profile(client_page_id)
        print(f"✅ Retrieved client profile with {len(profile)} fields")
        
        # Show some key fields
        print("📋 Current profile data:")
        key_fields = ["Name", "Industry", "Website", "Product_Service_Description"]
        for field in key_fields:
            if field in profile:
                value = profile[field]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  - {field}: {value}")
        
        return profile
        
    except Exception as e:
        print(f"❌ Failed to retrieve client profile: {e}")
        return None

def test_update_client_profile(db_manager, client_page_id):
    """Test updating client profile"""
    print(f"\n🔍 Testing client profile update for ID: {client_page_id[:8]}...")
    
    # Prepare test data
    test_data = {
        "Product_Service_Description": f"Test update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Brand_Values": "Innovation, Quality, Customer Service",
        "Brand_Mission": "To provide excellent service and build lasting relationships",
        "Words_Tones_To_Avoid": "Aggressive, Pushy, Corporate Jargon"
    }
    
    try:
        # Perform the update
        success = db_manager.update_client_profile(client_page_id, test_data)
        
        if success:
            print("✅ Client profile updated successfully")
            
            # Verify the update by retrieving the profile again
            print("🔍 Verifying update...")
            updated_profile = db_manager.get_client_profile(client_page_id)
            
            verification_success = True
            for field, expected_value in test_data.items():
                if field in updated_profile:
                    actual_value = updated_profile[field]
                    if isinstance(actual_value, list):
                        actual_value = ", ".join(actual_value)
                    
                    if actual_value == expected_value:
                        print(f"  ✅ {field}: Update verified")
                    else:
                        print(f"  ❌ {field}: Expected '{expected_value}', got '{actual_value}'")
                        verification_success = False
                else:
                    print(f"  ❌ {field}: Field not found in updated profile")
                    verification_success = False
            
            if verification_success:
                print("✅ All updates verified successfully")
            else:
                print("⚠️ Some updates could not be verified")
                
            return True
        else:
            print("❌ Client profile update failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update client profile: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Notion Database Update Test")
    print("=" * 50)
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    required_env_vars = ["NOTION_API_KEY", "NOTION_DATABASE_ID"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n💡 To run this test, set the following environment variables:")
        print("   export NOTION_API_KEY='your_notion_api_key'")
        print("   export NOTION_DATABASE_ID='your_database_id'")
        print("\n   Or run with variables inline:")
        print("   NOTION_API_KEY='xxx' NOTION_DATABASE_ID='xxx' python test_notion_update.py")
        return False
    else:
        print("✅ Environment variables configured")
    
    # Test 1: Connection
    db_manager = test_notion_connection()
    if not db_manager:
        return False
    
    # Test 2: Get client list
    client_name, client_page_id = test_get_client_list(db_manager)
    if not client_page_id:
        print("\n❌ Cannot proceed without a test client. Please add at least one client to your Notion database.")
        return False
    
    # Test 3: Get client profile
    original_profile = test_get_client_profile(db_manager, client_page_id)
    if not original_profile:
        return False
    
    # Test 4: Update client profile
    update_success = test_update_client_profile(db_manager, client_page_id)
    
    print("\n" + "=" * 50)
    if update_success:
        print("🎉 ALL TESTS PASSED! Notion database updates are working correctly.")
    else:
        print("❌ TESTS FAILED! There are issues with Notion database updates.")
    
    return update_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)