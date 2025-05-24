"""
Core framework module for research tools suite.
Provides shared components and utilities used by all research tools.
"""

import streamlit as st
from notion_client import Client
import json
import re
from datetime import datetime

class NotionDatabaseManager:
    """Centralized manager for Notion database operations"""
    def __init__(self, notion_api_key=None):
        """Initialize the Notion Database Manager"""
        if notion_api_key is None:
            notion_api_key = st.secrets["notion"]["NOTION_API_KEY"]
        
        self.notion = Client(auth=notion_api_key)
        self.client_database_id = st.secrets["notion"]["NOTION_DATABASE_ID"]
        
        # Get database IDs for content samples and voice guidelines
        self.content_samples_database_id = st.secrets["notion"]["Content_Samples_database_ID"]
        self.voice_guidelines_database_id = st.secrets["notion"]["voice_guidlines_database_id"]
    
    def get_client_list(self):
        """Get a list of all clients"""
        response = self.notion.databases.query(
            database_id=self.client_database_id,
            sorts=[
                {
                    "property": "Name",
                    "direction": "ascending"
                }
            ]
        )
        
        clients = {}
        for page in response["results"]:
            if "Name" in page["properties"] and page["properties"]["Name"]["title"]:
                client_name = page["properties"]["Name"]["title"][0]["text"]["content"]
                clients[client_name] = page["id"]
        
        return clients
    
    def create_new_client(self, client_name, industry):
        """Create a new client in the Notion database
        
        Args:
            client_name (str): Name of the client
            industry (str): Industry of the client
            
        Returns:
            str: The page ID of the newly created client
        """
        try:
            # Create the new client page
            response = self.notion.pages.create(
                parent={"database_id": self.client_database_id},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": client_name
                                }
                            }
                        ]
                    },
                    "Industry": {
                        "select": {
                            "name": industry
                        }
                    },
                    "Research_Status": {
                        "select": {
                            "name": "In Progress"
                        }
                    },
                    "Last_Updated": {
                        "date": {
                            "start": self._get_current_date()
                        }
                    }
                }
            )
            
            # Return the new page ID
            return response["id"]
        except Exception as e:
            st.error(f"Error creating new client: {str(e)}")
            return None
    
    def get_client_page_id(self, client_name):
        """Get the page ID for a client by name"""
        # Query the clients database
        response = self.notion.databases.query(
            database_id=self.client_database_id,
            filter={
                "property": "Name",
                "title": {
                    "equals": client_name
                }
            }
        )
        
        # Return the first matching page ID or None
        if response["results"]:
            return response["results"][0]["id"]
        return None
    
    def get_client_profile(self, client_page_id):
        """Get a client's profile data"""
        if not client_page_id:
            return {}
            
        try:
            # Retrieve the page
            page = self.notion.pages.retrieve(page_id=client_page_id)
            
            # Extract relevant properties
            profile = {"id": client_page_id}
            
            # Add properties to profile
            props = page.get("properties", {})
            
            # Basic properties
            if "Name" in props and props["Name"].get("title") and props["Name"]["title"]:
                profile["Name"] = props["Name"]["title"][0]["text"]["content"]
            
            if "Industry" in props and props["Industry"].get("select"):
                profile["Industry"] = props["Industry"]["select"]["name"]
            
            # Research properties
            rich_text_props = [
                "Product_Service_Description",
                "Current_Target_Audience",
                "Ideal_Target_Audience",
                "Brand_Mission",
                "Words_Tones_To_Avoid",
                "Website",
                "Contact_Email",
                "Phone_Number",
                "Address",
                "LinkedIn_URL",
                "Twitter_URL",
                "Facebook_URL",
                "Instagram_URL",
                "Other_Social_Media"
            ]
            
            for prop in rich_text_props:
                if prop in props and props[prop].get("rich_text") and props[prop]["rich_text"]:
                    profile[prop] = props[prop]["rich_text"][0]["text"]["content"]
            
            # Multi-select properties
            multi_select_props = [
                "Brand_Values",
                "Desired_Emotional_Impact",
                "Brand_Personality"
            ]
            
            for prop in multi_select_props:
                if prop in props and props[prop].get("multi_select"):
                    profile[prop] = [item["name"] for item in props[prop]["multi_select"]]
            
            # Tool status
            if "Research_Status" in props and props["Research_Status"].get("select"):
                profile["Research_Status"] = props["Research_Status"]["select"]["name"]
            else:
                profile["Research_Status"] = "Not Started"
            
            return profile
        except Exception as e:
            st.error(f"Error retrieving client profile: {str(e)}")
            return {}
    
    def update_client_profile(self, client_page_id, profile_data):
        """Update a client's profile with research data"""
        # Build properties dict from profile data
        properties = {
            "Research_Status": {
                "select": {
                    "name": "In Progress"
                }
            },
            "Last_Updated": {
                "date": {
                    "start": self._get_current_date()
                }
            }
        }
        
        # Add properties for rich text fields
        rich_text_fields = [
            "Product_Service_Description",
            "Current_Target_Audience", 
            "Ideal_Target_Audience", 
            "Brand_Mission", 
            "Words_Tones_To_Avoid",
            "Website",
            "Contact_Email",
            "Phone_Number",
            "Address",
            "LinkedIn_URL",
            "Twitter_URL",
            "Facebook_URL",
            "Instagram_URL",
            "Other_Social_Media"
        ]
        
        for field in rich_text_fields:
            if field in profile_data and profile_data[field]:
                properties[field] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": profile_data[field]
                            }
                        }
                    ]
                }
        
        # Handle multi-select fields
        multi_select_fields = [
            "Brand_Values",
            "Desired_Emotional_Impact",
            "Brand_Personality"
        ]
        
        for field in multi_select_fields:
            if field in profile_data and profile_data[field]:
                # If the data is a string, split it by commas
                if isinstance(profile_data[field], str):
                    values = [v.strip() for v in profile_data[field].split(",")]
                # If it's already a list, use it as is
                else:
                    values = profile_data[field]
                
                properties[field] = {
                    "multi_select": [{"name": value} for value in values]
                }
        
        # Update the page
        try:
            self.notion.pages.update(
                page_id=client_page_id,
                properties=properties
            )
            return True
        except Exception as e:
            st.error(f"Error updating client profile: {str(e)}")
            return False
    
    def get_tool_completion_status(self, client_page_id):
        """Get completion status of all tools for a client"""
        if not client_page_id:
            return {
                "context_gatherer": False,
                "content_collector": False,
                "voice_auditor": False,
                "audience_definer": False,
                "voice_traits_builder": False,
                "gap_analyzer": False,
                "content_rewriter": False,
                "guidelines_finalizer": False
            }
            
        try:
            # Retrieve the page
            page = self.notion.pages.retrieve(page_id=client_page_id)
            props = page.get("properties", {})
            
            # Extract status flags
            status = {
                "context_gatherer": False,
                "content_collector": False,
                "voice_auditor": False,
                "audience_definer": False,
                "voice_traits_builder": False,
                "gap_analyzer": False,
                "content_rewriter": False,
                "guidelines_finalizer": False
            }
            
            # Map property names to status keys
            prop_map = {
                "Context_Gatherer_Complete": "context_gatherer",
                "Content_Collector_Complete": "content_collector",
                "Voice_Auditor_Complete": "voice_auditor",
                "Audience_Definer_Complete": "audience_definer",
                "Voice_Traits_Builder_Complete": "voice_traits_builder",
                "Gap_Analyzer_Complete": "gap_analyzer",
                "Content_Rewriter_Complete": "content_rewriter",
                "Guidelines_Finalizer_Complete": "guidelines_finalizer"
            }
            
            # Check each property
            for prop_name, status_key in prop_map.items():
                if prop_name in props and props[prop_name].get("checkbox") is not None:
                    status[status_key] = props[prop_name]["checkbox"]
            
            return status
        except Exception as e:
            st.error(f"Error retrieving tool completion status: {str(e)}")
            # Return default status (all false)
            return {
                "context_gatherer": False,
                "content_collector": False,
                "voice_auditor": False,
                "audience_definer": False,
                "voice_traits_builder": False,
                "gap_analyzer": False,
                "content_rewriter": False,
                "guidelines_finalizer": False
            }
    
    def mark_tool_complete(self, client_page_id, tool_name):
        """Mark a specific tool as complete for a client"""
        # Map tool names to property names
        property_map = {
            "context_gatherer": "Context_Gatherer_Complete",
            "content_collector": "Content_Collector_Complete",
            "voice_auditor": "Voice_Auditor_Complete",
            "audience_definer": "Audience_Definer_Complete",
            "voice_traits_builder": "Voice_Traits_Builder_Complete",
            "gap_analyzer": "Gap_Analyzer_Complete",
            "content_rewriter": "Content_Rewriter_Complete",
            "guidelines_finalizer": "Guidelines_Finalizer_Complete"
        }
        
        # Update the property
        if tool_name in property_map:
            try:
                self.notion.pages.update(
                    page_id=client_page_id,
                    properties={
                        property_map[tool_name]: {
                            "checkbox": True
                        },
                        "Last_Tool_Completed": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": tool_name
                                    }
                                }
                            ]
                        },
                        "Last_Updated": {
                            "date": {
                                "start": self._get_current_date()
                            }
                        }
                    }
                )
                return True
            except Exception as e:
                st.error(f"Error marking tool complete: {str(e)}")
                return False
        else:
            return False
    
    def _get_current_date(self):
        """Get current date in ISO format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    # Content samples methods - stub implementations for now
    def add_content_samples(self, client_page_id, samples_data):
        """Add content samples"""
        # This will be implemented fully when we build the Content Collector tool
        pass
    
    def get_content_samples(self, client_page_id):
        """Get content samples for a client"""
        # This will be implemented fully when we build the Content Collector tool
        return []
    
    # Voice guidelines methods - stub implementations for now
    def update_voice_guidelines(self, client_page_id, voice_data):
        """Update voice guidelines"""
        # This will be implemented fully when we build the Voice-related tools
        pass
    
    def get_voice_guidelines(self, client_page_id):
        """Get voice guidelines for a client"""
        # This will be implemented fully when we build the Voice-related tools
        return {}


def client_selector_sidebar(db_manager=None, allow_new_client=False):
    """Shared client selector sidebar component with option to create new client
    
    Args:
        db_manager (NotionDatabaseManager, optional): Database manager instance. Defaults to None.
        allow_new_client (bool, optional): Whether to allow creating new clients. Defaults to False.
        
    Returns:
        tuple: (client_page_id, selected_client, status)
    """
    # Initialize database manager if not provided
    if db_manager is None:
        db_manager = NotionDatabaseManager()
    
    # Get client list
    client_list = db_manager.get_client_list()
    
    # Create options for the dropdown
    client_options = list(client_list.keys())
    
    # Add "Create New Client" option if allowed
    if allow_new_client:
        client_options = ["➕ Create New Client"] + client_options
    
    # Display a message if no clients and not allowing new clients
    if not client_options and not allow_new_client:
        st.sidebar.warning("No clients found in Notion database. Please add clients directly in Notion.")
        return None, None, {}
    
    # Select client from dropdown
    selected_client = st.sidebar.selectbox(
        "Select Client",
        options=client_options,
        key="research_client_selector"
    )
    
    # Handle new client creation
    if selected_client == "➕ Create New Client":
        with st.sidebar.form("new_client_form"):
            st.subheader("Create New Client")
            new_client_name = st.text_input("Client Name", key="new_client_name")
            website_url = st.text_input("Website URL (optional)", key="new_client_website", 
                                      help="Provide URL to auto-extract company information")
            
            create_button = st.form_submit_button("Create Client")
            
            if create_button and new_client_name:
                # Import analysis functions if website URL provided
                if website_url.strip():
                    # Import the analysis functions from context_gatherer
                    try:
                        from tools.context_gatherer import extract_website_data, analyze_brand_voice
                        
                        # Step 1: Extract website data
                        with st.spinner("Step 1: Extracting company data from website..."):
                            step1_success, website_data, step1_error = extract_website_data(new_client_name, website_url.strip())
                            
                        if step1_success:
                            st.sidebar.success("✅ Step 1 complete: Company data extracted")
                            
                            # Step 2: Analyze brand voice
                            with st.spinner("Step 2: Analyzing brand voice..."):
                                step2_success, analysis_result, step2_error = analyze_brand_voice(new_client_name, website_data)
                                
                            if step2_success:
                                st.sidebar.success("✅ Step 2 complete: Brand voice analysis finished")
                                success = True
                                error_msg = None
                            else:
                                st.sidebar.error(f"Step 2 failed: {step2_error}")
                                success = False
                                analysis_result = website_data  # Use partial data
                                error_msg = step2_error
                        else:
                            st.sidebar.error(f"Step 1 failed: {step1_error}")
                            success = False
                            analysis_result = None
                            error_msg = step1_error
                        
                        if success:
                            # Use extracted industry and data
                            new_client_industry = analysis_result.get("industry", "Other")
                            extracted_data = analysis_result
                            st.sidebar.success("✅ Website analyzed successfully!")
                        else:
                            st.sidebar.error(f"Website analysis failed: {error_msg}")
                            new_client_industry = "Other"
                            extracted_data = None
                    except Exception as e:
                        st.sidebar.error(f"Analysis failed: {str(e)}")
                        new_client_industry = "Other"
                        extracted_data = None
                else:
                    # No website provided, use default
                    new_client_industry = "Other"
                    extracted_data = None
                
                # Create the new client
                new_client_id = db_manager.create_new_client(new_client_name, new_client_industry)
                
                # If we have extracted data, update the client profile immediately
                if new_client_id and extracted_data:
                    # Map analysis results to Notion fields
                    notion_data = {
                        "Industry": extracted_data.get("industry", "Other"),
                        "Website": website_url.strip(),
                        "Product_Service_Description": extracted_data.get("product_service_description", ""),
                        "Current_Target_Audience": extracted_data.get("current_target_audience", ""),
                        "Ideal_Target_Audience": extracted_data.get("ideal_target_audience", ""),
                        "Brand_Values": extracted_data.get("brand_values", ""),
                        "Brand_Mission": extracted_data.get("brand_mission", ""),
                        "Desired_Emotional_Impact": extracted_data.get("desired_emotional_impact", ""),
                        "Brand_Personality": extracted_data.get("brand_personality", ""),
                        "Words_Tones_To_Avoid": extracted_data.get("words_tones_to_avoid", ""),
                        "Contact_Email": extracted_data.get("contact_email", ""),
                        "Phone_Number": extracted_data.get("phone_number", ""),
                        "Address": extracted_data.get("address", ""),
                        "LinkedIn_URL": extracted_data.get("linkedin_url", ""),
                        "Twitter_URL": extracted_data.get("twitter_url", ""),
                        "Facebook_URL": extracted_data.get("facebook_url", ""),
                        "Instagram_URL": extracted_data.get("instagram_url", ""),
                        "Other_Social_Media": extracted_data.get("other_social_media", "")
                    }
                    
                    # Update the client profile with extracted data
                    db_manager.update_client_profile(new_client_id, notion_data)
                elif new_client_id and website_url.strip():
                    # No analysis but website provided, store the URL
                    db_manager.update_client_profile(new_client_id, {"Website": website_url.strip()})
                
                if new_client_id:
                    # Store in session state for continued use
                    st.session_state.client_page_id = new_client_id
                    st.session_state.client_name = new_client_name
                    
                    # Show success message and refresh
                    st.sidebar.success(f"✅ Created new client: {new_client_name}")
                    
                    # Return the new client info
                    return new_client_id, new_client_name, {
                        "context_gatherer": False,
                        "content_collector": False,
                        "voice_auditor": False,
                        "audience_definer": False,
                        "voice_traits_builder": False,
                        "gap_analyzer": False,
                        "content_rewriter": False,
                        "guidelines_finalizer": False
                    }
                else:
                    st.sidebar.error("Failed to create new client")
        
        # If we reach here, no client was created yet
        return None, None, {}
    
    # Handle existing client selection
    elif selected_client in client_list:
        client_page_id = client_list[selected_client]
        
        # Store in session state
        st.session_state.client_page_id = client_page_id
        st.session_state.client_name = selected_client
        
        # Show tool completion status
        try:
            status = db_manager.get_tool_completion_status(client_page_id)
            
            st.sidebar.markdown("### Research Progress")
            status_emojis = {True: "✅", False: "⬜"}
            
            tool_labels = [
                ("context_gatherer", "1. Context Gatherer"),
                ("content_collector", "2. Content Collector"),
                ("voice_auditor", "3. Voice Auditor"),
                ("audience_definer", "4. Audience Definer"),
                ("voice_traits_builder", "5. Voice Traits Builder"),
                ("gap_analyzer", "6. Gap Analyzer"),
                ("content_rewriter", "7. Content Rewriter"),
                ("guidelines_finalizer", "8. Guidelines Finalizer")
            ]
            
            for key, label in tool_labels:
                st.sidebar.markdown(f"{status_emojis[status.get(key, False)]} {label}")
        
        except Exception as e:
            st.sidebar.warning("Could not retrieve tool status.")
            status = {}
        
        return client_page_id, selected_client, status
    else:
        # No valid selection
        st.sidebar.warning("Please select a client or create a new one.")
        return None, None, {}


def check_prerequisites(status, required_tools):
    """Check if prerequisites are completed"""
    if not status:
        return False, required_tools
    
    missing = [tool for tool in required_tools if not status.get(tool, False)]
    return len(missing) == 0, missing


def format_list_for_display(items_list):
    """Format a list for display (converts list to comma-separated string)"""
    if not items_list:
        return ""
    
    if isinstance(items_list, list):
        return ", ".join(items_list)
    
    return str(items_list)


def parse_markdown_table(markdown_table):
    """Parse a markdown table into a list of dictionaries"""
    result = []
    
    # Split into lines
    lines = markdown_table.strip().split('\n')
    
    # Find header row
    header_row = None
    for i, line in enumerate(lines):
        if line.startswith('|') and i < len(lines) - 1 and re.match(r'^\|\s*[-:]+\s*\|', lines[i+1]):
            header_row = line
            break
    
    if not header_row:
        return result
    
    # Extract headers
    headers = [h.strip() for h in header_row.split('|')[1:-1]]
    
    # Process data rows
    for line in lines:
        # Skip header and separator rows
        if line == header_row or re.match(r'^\|\s*[-:]+\s*\|', line):
            continue
        
        # Extract cells
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            # Skip if the number of cells doesn't match headers
            if len(cells) != len(headers):
                continue
            
            # Create a dictionary for this row
            row_dict = {headers[i]: cells[i] for i in range(len(headers))}
            result.append(row_dict)
    
    return result

def get_context_gatherer_schema():
    """
    Get the schema for Context Gatherer structured output
    """
    return {
        "type": "object",
        "properties": {
            "business_name": {"type": "string", "description": "The name of the business"},
            "industry": {"type": "string", "description": "The industry sector of the business"},
            "product_service_description": {"type": "string", "description": "Description of what the client offers"},
            "current_target_audience": {"type": "string", "description": "Who the client currently reaches"},
            "ideal_target_audience": {"type": "string", "description": "Who the client ideally wants to reach"},
            "brand_values": {"type": "string", "description": "Core principles that guide the brand (comma-separated)"},
            "brand_mission": {"type": "string", "description": "The brand's purpose or reason for existing"},
            "desired_emotional_impact": {"type": "string", "description": "How audience should feel (comma-separated)"},
            "brand_personality": {"type": "string", "description": "3-5 adjectives describing the brand as a person"},
            "words_tones_to_avoid": {"type": "string", "description": "Language or topics to stay away from"}
        },
        "required": [
            "business_name", 
            "industry", 
            "product_service_description",
            "current_target_audience",
            "ideal_target_audience",
            "brand_values",
            "brand_mission",
            "desired_emotional_impact",
            "brand_personality"
        ],
        "propertyOrdering": [
            "business_name",
            "industry",
            "product_service_description",
            "current_target_audience",
            "ideal_target_audience",
            "brand_values",
            "brand_mission",
            "desired_emotional_impact",
            "brand_personality",
            "words_tones_to_avoid"
        ]
    }

def get_content_collector_schema():
    """
    Get the schema for Content Collector structured output
    """
    return {
        "type": "object",
        "properties": {
            "content_samples": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "description": "The type of content or platform"},
                        "content": {"type": "string", "description": "The sample content text"},
                        "notes": {"type": "string", "description": "Optional notes about the content"}
                    },
                    "required": ["channel", "content"],
                    "propertyOrdering": ["channel", "content", "notes"]
                }
            }
        },
        "required": ["content_samples"],
    }