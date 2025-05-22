#!/usr/bin/env python3
"""
Create Notion Databases Script for Jon's AI Tools

This script creates the Content Samples and Voice Guidelines databases
in an existing Notion page.

Usage:
1. Create a blank page in Notion where you want the databases to be created
2. Copy the page ID from the URL (the part after the workspace name and before any ?)
3. Run the script: python create_databases.py [page_id]
"""

import sys
import json
from notion_client import Client

# Configuration
NOTION_API_KEY = "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"
CLIENT_DATABASE_ID = "1f872022-1e76-81f2-8248-e812a9295df0"

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def main():
    # Check if a page ID was provided
    if len(sys.argv) < 2:
        print("Please provide the Notion page ID where databases should be created.")
        print("Usage: python create_databases.py [page_id]")
        print("\nHow to get the page ID:")
        print("1. Create a blank page in Notion")
        print("2. Copy the ID from the URL: https://www.notion.so/workspace/[page-id]?...")
        sys.exit(1)
    
    page_id = sys.argv[1]
    
    print(f"Using page ID: {page_id}")
    print(f"Using client database ID: {CLIENT_DATABASE_ID}")
    
    # Initialize Notion client
    try:
        print(f"Initializing Notion client...")
        notion = Client(auth=NOTION_API_KEY)
        print("Successfully initialized Notion client")
        
        # Verify the page exists
        try:
            page = notion.pages.retrieve(page_id=page_id)
            print(f"Found page: {page.get('id')}")
        except Exception as e:
            print(f"Error retrieving page: {str(e)}")
            print("Please make sure the page ID is correct and you have permission to access it.")
            sys.exit(1)
        
        # Create Content Samples database
        print_header("Creating Content Samples Database")
        
        print("Creating Content Samples database...")
        response = notion.databases.create(
            parent={"type": "page_id", "page_id": page_id},
            title=[
                {
                    "type": "text",
                    "text": {
                        "content": "Content Samples"
                    }
                }
            ],
            properties={
                "Name": {
                    "title": {}
                },
                "Client": {
                    "type": "relation",
                    "relation": {
                        "database_id": CLIENT_DATABASE_ID,
                        "single_property": {}
                    }
                },
                "Channel_Type": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Website Homepage", "color": "blue"},
                            {"name": "Website About", "color": "blue"},
                            {"name": "Website Services", "color": "blue"},
                            {"name": "Instagram", "color": "pink"},
                            {"name": "Facebook", "color": "purple"},
                            {"name": "LinkedIn", "color": "blue"},
                            {"name": "Twitter", "color": "blue"},
                            {"name": "Email Newsletter", "color": "yellow"},
                            {"name": "Blog", "color": "green"},
                            {"name": "Customer Service", "color": "orange"},
                            {"name": "Other", "color": "gray"}
                        ]
                    }
                },
                "Sample_Content": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Tone_Assessment": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "For Review", "color": "gray"},
                            {"name": "Excellent", "color": "green"},
                            {"name": "Good", "color": "blue"},
                            {"name": "Needs Improvement", "color": "orange"}
                        ]
                    }
                },
                "Original_Sample": {
                    "type": "checkbox",
                    "checkbox": {}
                },
                "Rewritten_Version": {
                    "type": "checkbox",
                    "checkbox": {}
                },
                "Notes": {
                    "type": "rich_text",
                    "rich_text": {}
                }
            }
        )
        
        # Get the new database ID
        content_samples_database_id = response["id"]
        print(f"✅ Created Content Samples database with ID: {content_samples_database_id}")
        
        # Create Voice Guidelines database
        print_header("Creating Voice Guidelines Database")
        
        print("Creating Voice Guidelines database...")
        response = notion.databases.create(
            parent={"type": "page_id", "page_id": page_id},
            title=[
                {
                    "type": "text",
                    "text": {
                        "content": "Voice Guidelines"
                    }
                }
            ],
            properties={
                "Name": {
                    "title": {}
                },
                "Client": {
                    "type": "relation",
                    "relation": {
                        "database_id": CLIENT_DATABASE_ID,
                        "single_property": {}
                    }
                },
                "Status": {
                    "type": "select",
                    "select": {
                        "options": [
                            {"name": "Draft", "color": "yellow"},
                            {"name": "In Progress", "color": "blue"},
                            {"name": "Final", "color": "green"},
                            {"name": "Archived", "color": "gray"}
                        ]
                    }
                },
                "Last_Updated": {
                    "type": "date",
                    "date": {}
                },
                
                # Voice Audit Data
                "Word_Choice_Analysis": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Tone_Analysis": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Personality_Analysis": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Consistency_Assessment": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Audience_Fit_Assessment": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                
                # Voice Traits
                "Voice_Traits": {
                    "type": "multi_select",
                    "multi_select": {
                        "options": []  # Will be populated by users
                    }
                },
                "Tone_Description": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Word_Choice_Guidelines": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Signature_Phrases": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                
                # Gap Analysis
                "Identified_Gaps": {
                    "type": "rich_text",
                    "rich_text": {}
                },
                "Recommendations": {
                    "type": "rich_text",
                    "rich_text": {}
                }
            }
        )
        
        voice_guidelines_database_id = response["id"]
        print(f"✅ Created Voice Guidelines database with ID: {voice_guidelines_database_id}")
        
        # Summary
        print_header("Setup Complete")
        print("Both databases created successfully!")
        print(f"Content Samples database ID: {content_samples_database_id}")
        print(f"Voice Guidelines database ID: {voice_guidelines_database_id}")
        
        print("\nAdd these IDs to your secrets.toml file:")
        print(f"Content_Samples_database_ID = \"{content_samples_database_id}\"")
        print(f"voice_guidlines_database_id = \"{voice_guidelines_database_id}\"")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()