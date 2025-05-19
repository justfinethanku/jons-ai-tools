# create_notion_database_fixed.py
from notion_client import Client

NOTION_TOKEN = "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"

def create_database_in_page():
    """Create database with proper search"""
    notion = Client(auth=NOTION_TOKEN)
    
    try:
        # Fixed search - remove the problematic filter
        search_results = notion.search()
        
        print("Available items as parents:")
        pages = []
        for i, item in enumerate(search_results["results"][:10]):
            if item["object"] == "page":  # Only show pages, not databases
                title = "Untitled"
                if "properties" in item and "title" in item["properties"]:
                    if item["properties"]["title"]["title"]:
                        title = item["properties"]["title"]["title"][0]["plain_text"]
                elif "title" in item:
                    if item["title"]:
                        title = item["title"][0]["plain_text"]
                
                print(f"{len(pages)+1}. {title} (ID: {item['id']})")
                pages.append(item)
        
        if not pages:
            print("No pages found. Create a regular page in Notion first.")
            return None
        
        # Use the first page as parent
        parent_page = pages[0]
        print(f"\nUsing parent page: {parent_page['id']}")
        
        # Database schema
        database_properties = {
            "Name": {"title": {}},
            "Brand Voice": {"rich_text": {}},
            "Tone": {
                "select": {
                    "options": [
                        {"name": "Professional", "color": "blue"},
                        {"name": "Casual", "color": "green"},
                        {"name": "Friendly", "color": "yellow"},
                        {"name": "Authoritative", "color": "red"},
                        {"name": "Playful", "color": "purple"}
                    ]
                }
            },
            "Industry": {
                "select": {
                    "options": [
                        {"name": "Technology", "color": "blue"},
                        {"name": "Healthcare", "color": "green"},
                        {"name": "Finance", "color": "yellow"},
                        {"name": "E-commerce", "color": "orange"},
                        {"name": "Education", "color": "purple"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "Target Audience": {"rich_text": {}},
            "Custom Prompts": {"rich_text": {}},
            "Keywords": {
                "multi_select": {
                    "options": [
                        {"name": "Innovation", "color": "blue"},
                        {"name": "Quality", "color": "green"},
                        {"name": "Affordable", "color": "yellow"},
                        {"name": "Premium", "color": "red"},
                        {"name": "Fast", "color": "orange"}
                    ]
                }
            }
        }
        
        # Create the database
        response = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page["id"]},
            title=[{"type": "text", "text": {"content": "AI Client Library"}}],
            properties=database_properties
        )
        
        database_id = response["id"]
        print(f"✅ Database created successfully!")
        print(f"Database ID: {database_id}")
        print(f"🔗 Database URL: https://notion.so/{database_id.replace('-', '')}")
        
        # Add sample clients
        add_sample_clients(notion, database_id)
        
        return database_id
        
    except Exception as e:
        print(f"❌ Failed to create database: {str(e)}")
        return None

def add_sample_clients(notion, database_id):
    """Add sample clients"""
    clients = [
        {
            "Name": "Acme Corp",
            "Brand Voice": "Professional and technical, focused on innovation",
            "Tone": "Professional",
            "Industry": "Technology",
            "Target Audience": "Software developers and tech decision makers",
            "Custom Prompts": "Always mention cutting-edge technology and ROI",
            "Keywords": ["Innovation", "Quality"]
        },
        {
            "Name": "HealthPlus Clinic", 
            "Brand Voice": "Caring, trustworthy, and empathetic",
            "Tone": "Friendly",
            "Industry": "Healthcare",
            "Target Audience": "Patients and their families",
            "Custom Prompts": "Focus on patient care and trust-building",
            "Keywords": ["Quality", "Premium"]
        }
    ]
    
    for client in clients:
        try:
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": {"title": [{"text": {"content": client["Name"]}}]},
                    "Brand Voice": {"rich_text": [{"text": {"content": client["Brand Voice"]}}]},
                    "Tone": {"select": {"name": client["Tone"]}},
                    "Industry": {"select": {"name": client["Industry"]}},
                    "Target Audience": {"rich_text": [{"text": {"content": client["Target Audience"]}}]},
                    "Custom Prompts": {"rich_text": [{"text": {"content": client["Custom Prompts"]}}]},
                    "Keywords": {"multi_select": [{"name": keyword} for keyword in client["Keywords"]]}
                }
            )
            print(f"✅ Added client: {client['Name']}")
        except Exception as e:
            print(f"❌ Failed to add client {client['Name']}: {str(e)}")

if __name__ == "__main__":
    database_id = create_database_in_page()
    if database_id:
        print(f"\n🎉 SUCCESS! Your AI Client Library is ready!")
        print(f"Database ID: {database_id}")
        print("Copy this ID for your Streamlit integration!")