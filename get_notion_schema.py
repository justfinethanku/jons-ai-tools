"""
Simple Notion Schema Puller
Pulls actual schema from Notion databases and saves to markdown file
"""

from notion_client import Client
from datetime import datetime
import json

def pull_notion_schema(api_key: str, output_file: str = "NOTION_DATABASE_SCHEMA.md"):
    """
    Pull schema from Notion databases and save to markdown file
    
    Args:
        api_key: Your Notion API key
        output_file: Output markdown filename
    """
    
    # Initialize Notion client
    notion = Client(auth=api_key)
    
    # Database IDs
    databases = {
        "AI Client Library": {
            "id": "1fd72022-1e76-81ce-9f16-e77cd8075e3b",
            "purpose": "Central client management and workflow tracking"
        },
        "Content Samples": {
            "id": "1fd72022-1e76-8119-9f36-d4ce24c04d86", 
            "purpose": "Store and analyze client content for voice development"
        },
        "Voice Guidelines": {
            "id": "1fd72022-1e76-8117-9d2f-ed89252b6bc3",
            "purpose": "Comprehensive brand voice documentation and guidelines"
        }
    }
    
    # Start building markdown content
    md_content = []
    md_content.append("# Notion Database Schema Reference")
    md_content.append(f"\n*Auto-generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md_content.append("\n## Database Overview\n")
    md_content.append("The system uses three interconnected Notion databases:\n")
    
    for i, (name, info) in enumerate(databases.items(), 1):
        md_content.append(f"{i}. **{name}** - {info['purpose']}")
    
    # Pull schema for each database
    for db_name, db_info in databases.items():
        print(f"Pulling schema for {db_name}...")
        
        try:
            # Get database details
            database = notion.databases.retrieve(database_id=db_info['id'])
            
            # Add database section
            md_content.append(f"\n## 📋 {db_name}")
            md_content.append(f"**Database ID**: `{db_info['id']}`  ")
            md_content.append(f"**Purpose**: {db_info['purpose']}\n")
            md_content.append("### Properties\n")
            md_content.append("| Property | Type | Description | Options/Details |")
            md_content.append("|----------|------|-------------|-----------------|")
            
            # Sort properties for consistent output
            properties = sorted(database.get('properties', {}).items())
            
            for prop_name, prop_config in properties:
                prop_type = prop_config.get('type', 'unknown')
                
                # Build options/details column
                details = []
                
                if prop_type == 'select':
                    options = [opt['name'] for opt in prop_config.get('select', {}).get('options', [])]
                    if options:
                        details.append(", ".join(options))
                
                elif prop_type == 'multi_select':
                    options = [opt['name'] for opt in prop_config.get('multi_select', {}).get('options', [])]
                    if options:
                        details.append(", ".join(options))
                
                elif prop_type == 'relation':
                    relation_info = prop_config.get('relation', {})
                    if relation_info.get('database_id'):
                        # Find which database this relates to
                        related_db = "Unknown"
                        for db, info in databases.items():
                            if info['id'] == relation_info['database_id']:
                                related_db = db
                                break
                        details.append(f"Links to {related_db}")
                
                elif prop_type == 'rollup':
                    rollup_info = prop_config.get('rollup', {})
                    func = rollup_info.get('function', '')
                    details.append(f"Calculated from {rollup_info.get('relation_property_name', 'related property')}")
                
                elif prop_type == 'formula':
                    details.append("Calculated field")
                
                elif prop_type == 'created_time':
                    details.append("Auto-generated")
                
                elif prop_type == 'last_edited_time':
                    details.append("Auto-generated")
                
                elif prop_type == 'title':
                    details.append("Primary identifier")
                
                # Description placeholder - you can customize these
                description = {
                    'Name': 'Primary identifier',
                    'Client': 'Links to client record',
                    'Status': 'Current status',
                    'Website': 'Company website URL',
                    'Industry': 'Business sector',
                    'Last_Updated': 'Last modification date'
                }.get(prop_name, '')
                
                # Format property name (make it bold)
                formatted_name = f"**{prop_name}**"
                
                # Add row
                details_str = details[0] if details else ""
                md_content.append(f"| {formatted_name} | {prop_type} | {description} | {details_str} |")
            
            print(f"✅ Successfully pulled schema for {db_name}")
            
        except Exception as e:
            print(f"❌ Error pulling schema for {db_name}: {str(e)}")
            md_content.append(f"\n*Error retrieving schema: {str(e)}*\n")
    
    # Add relationships section
    md_content.append("\n## Database Relationships\n")
    md_content.append("```")
    md_content.append("AI Client Library (Main)")
    md_content.append("├── Content_Samples (relation) → Content Samples Database")
    md_content.append("├── Voice_Guidelines (relation) → Voice Guidelines Database")
    md_content.append("└── Project_Tracker (relation) → Project Tracker Database")
    md_content.append("")
    md_content.append("Content Samples Database")
    md_content.append("└── Client (relation) → AI Client Library")
    md_content.append("")
    md_content.append("Voice Guidelines Database")
    md_content.append("└── Client (relation) → AI Client Library")
    md_content.append("```")
    
    # Add configuration section
    md_content.append("\n## Access Configuration\n")
    md_content.append("All databases are accessed via the Notion integration:\n")
    md_content.append("```toml")
    md_content.append("[notion]")
    md_content.append(f'NOTION_API_KEY = "your-notion-integration-token"')
    md_content.append(f'NOTION_DATABASE_ID = "{databases["AI Client Library"]["id"]}"  # AI Client Library')
    md_content.append(f'Content_Samples_database_ID = "{databases["Content Samples"]["id"]}"')
    md_content.append(f'voice_guidelines_database_id = "{databases["Voice Guidelines"]["id"]}"')
    md_content.append("```")
    
    # Add footer
    md_content.append(f"\n---\n")
    md_content.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d')}*  ")
    md_content.append(f"*Generated by Notion Schema Puller*")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"\n✅ Schema documentation saved to: {output_file}")
    
    # Also create a JSON version for programmatic use
    json_filename = output_file.replace('.md', '.json')
    schema_json = {}
    
    for db_name, db_info in databases.items():
        try:
            database = notion.databases.retrieve(database_id=db_info['id'])
            schema_json[db_name] = {
                'id': db_info['id'],
                'properties': {}
            }
            
            for prop_name, prop_config in database.get('properties', {}).items():
                prop_type = prop_config.get('type')
                prop_data = {'type': prop_type}
                
                if prop_type == 'select':
                    prop_data['options'] = [opt['name'] for opt in prop_config.get('select', {}).get('options', [])]
                elif prop_type == 'multi_select':
                    prop_data['options'] = [opt['name'] for opt in prop_config.get('multi_select', {}).get('options', [])]
                elif prop_type == 'relation':
                    prop_data['database_id'] = prop_config.get('relation', {}).get('database_id')
                
                schema_json[db_name]['properties'][prop_name] = prop_data
                
        except Exception as e:
            schema_json[db_name] = {'error': str(e)}
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(schema_json, f, indent=2)
    
    print(f"✅ Schema JSON saved to: {json_filename}")
    
    return schema_json


# If running directly
if __name__ == "__main__":
    # You need to provide your Notion API key
    API_KEY = input("Enter your Notion API key: ").strip()
    
    if API_KEY:
        pull_notion_schema(API_KEY)
    else:
        print("❌ No API key provided")