"""
Context Gatherer Tool - First step in the research workflow.
Collects foundational client information and brand attributes.
Allows creating new clients and enhancing existing ones.
"""

import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import trafilatura
from frameworks import universal_framework, research_tools_framework

def extract_content_from_url(url):
    """
    Extract text content from a URL
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: The extracted text content
    """
    try:
        # Use trafilatura for effective text extraction (handles most modern websites well)
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if extracted_text:
                return extracted_text
        
        # Fallback to BeautifulSoup if trafilatura fails
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        else:
            return f"Error: Unable to access the URL (Status code: {response.status_code})"
    except Exception as e:
        return f"Error extracting content from URL: {str(e)}"

def research_missing_information(client_name, industry, website_url=None, minimal_info=None):
    """
    Research missing information about a client using LLM
    
    Args:
        client_name: The name of the client
        industry: The industry of the client
        website_url: Optional URL to the client's website
        minimal_info: Any minimal information already provided
        
    Returns:
        dict: Researched information about the client
    """
    with st.spinner("Researching client information..."):
        # Create the research prompt
        prompt = f"""As an AI research assistant, I need comprehensive information about a company called "{client_name}" in the {industry} industry.

Please research and provide the following information in a structured format:

1. Brief description of what {client_name} offers (products/services)
2. Their current target audience (demographics, interests, pain points)
3. Who would be their ideal target audience (may differ from current)
4. Core brand values (3-5 key principles)
5. Brand mission or purpose statement
6. What emotional impact they likely want to have on their audience
7. Brand personality traits (3-5 adjectives that describe their brand as if it were a person)
8. Topics or language they likely want to avoid

"""
        # Add website content if provided
        if website_url:
            website_content = extract_content_from_url(website_url)
            if website_content and not website_content.startswith("Error"):
                # Truncate if too long (to fit context window)
                if len(website_content) > 10000:
                    website_content = website_content[:10000] + "...[content truncated]"
                
                prompt += f"""
I have extracted the following text from their website ({website_url}). Use this information to inform your response:

WEBSITE CONTENT:
{website_content}

"""
        
        # Add any known information
        if minimal_info:
            prompt += f"""
I already know the following information, so focus on filling in the gaps:
{minimal_info}
"""
        
        prompt += """
Make educated guesses based on industry standards and best practices when specific information isn't available. 
Format your response as a structured JSON object with these keys:
- product_service_description
- current_target_audience
- ideal_target_audience
- brand_values (comma-separated)
- brand_mission
- desired_emotional_impact (comma-separated)
- brand_personality (comma-separated)
- words_tones_to_avoid

For example:
{
  "product_service_description": "Brief description",
  "current_target_audience": "Current audience description",
  "ideal_target_audience": "Ideal audience description",
  "brand_values": "Value1, Value2, Value3",
  "brand_mission": "Mission statement",
  "desired_emotional_impact": "Emotion1, Emotion2, Emotion3",
  "brand_personality": "Trait1, Trait2, Trait3",
  "words_tones_to_avoid": "Topics to avoid"
}
"""
        
        # Call LLM to research the information
        try:
            # Try with structured output first
            schema = {
                "type": "object",
                "properties": {
                    "product_service_description": {"type": "string"},
                    "current_target_audience": {"type": "string"},
                    "ideal_target_audience": {"type": "string"},
                    "brand_values": {"type": "string"},
                    "brand_mission": {"type": "string"},
                    "desired_emotional_impact": {"type": "string"},
                    "brand_personality": {"type": "string"},
                    "words_tones_to_avoid": {"type": "string"}
                },
                "required": [
                    "product_service_description",
                    "current_target_audience",
                    "ideal_target_audience",
                    "brand_values",
                    "brand_mission", 
                    "desired_emotional_impact",
                    "brand_personality"
                ]
            }
            response = universal_framework.call_gemini_api(prompt, response_schema=schema)
            
            # Parse the JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to GPT-4 if Gemini response has issues
                response = universal_framework.call_openai_api(prompt)
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON content
                    if "{" in response and "}" in response:
                        json_content = response[response.find("{"):response.rfind("}")+1]
                        return json.loads(json_content)
                except:
                    # If all parsing fails, return empty dict
                    st.warning("Could not parse research results. Please fill in the information manually.")
                    return {}
                    
        except Exception as e:
            st.error(f"Error researching client information: {str(e)}")
            return {}

def optimize_content_for_next_steps(input_data):
    """
    Optimize the collected content to make it more suitable for the next steps in the workflow
    
    Args:
        input_data (dict): The raw input data
        
    Returns:
        dict: Optimized data
    """
    # Create a prompt for content optimization
    fields_to_optimize = []
    
    for field, value in input_data.items():
        if value and len(value) > 5:  # Only include non-empty fields
            fields_to_optimize.append(f"{field}: {value}")
    
    if not fields_to_optimize:
        return input_data  # Nothing to optimize
    
    prompt = f"""As a brand voice and content expert, I need to rewrite and optimize the following client information to make it more useful for brand voice development. 

The optimized content should:
1. Be clear, concise, and specific
2. Use industry-standard terminology 
3. Highlight distinctive brand attributes
4. Avoid generic statements when possible
5. Maintain the original meaning but improve clarity and precision

Here's the content to optimize:

{chr(10).join(fields_to_optimize)}

Optimize each field and return the results in a structured JSON format, using the same field names as in the input.
"""
    
    # Call LLM to optimize the content
    try:
        schema = {
            "type": "object",
            "properties": {
                field: {"type": "string"} for field in input_data.keys() if input_data[field]
            }
        }
        
        response = universal_framework.call_gemini_api(prompt, response_schema=schema)
        
        try:
            optimized_data = json.loads(response)
            
            # Merge the optimized data with the original data
            # (only replace fields that were optimized)
            result = input_data.copy()
            for field, value in optimized_data.items():
                if field in result:
                    result[field] = value
            
            return result
        except:
            # If parsing fails, return original data
            return input_data
    except:
        return input_data

def get_fixed_context_gatherer_schema():
    """
    Get a fixed schema for Context Gatherer structured output
    (without the propertyOrdering field that causes issues)
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
        ]
        # Removed propertyOrdering field
    }

def run_context_gatherer():
    st.title("Context Gatherer")
    st.write("Collect foundational client information and brand attributes")
    
    # Initialize Notion database manager
    db_manager = research_tools_framework.NotionDatabaseManager()
    
    # Client selector sidebar with option to create new clients
    client_page_id, selected_client, status = research_tools_framework.client_selector_sidebar(
        db_manager=db_manager, 
        allow_new_client=True
    )
    
    if not client_page_id:
        st.info("Please select a client from the sidebar or create a new one to get started.")
        
        # Show instructions for new users
        with st.expander("How to use the Context Gatherer"):
            st.markdown("""
            ### Getting Started
            
            The Context Gatherer is the first step in developing a client's brand voice. Here's how to use it:
            
            1. **Create a new client** using the sidebar dropdown
            2. **Fill in the client information** form with as much detail as possible
            3. **Generate a context summary** to save the information to Notion
            4. **Review and save** the generated content to Notion
            
            This tool helps establish the foundation for all subsequent brand voice research steps.
            """)
        return
    
    try:
        # Pre-fill form with existing data if available
        client_profile = db_manager.get_client_profile(client_page_id)
        
        # Store current values in session state
        if "product_service" not in st.session_state:
            st.session_state.product_service = client_profile.get("Product_Service_Description", "")
        if "current_audience" not in st.session_state:
            st.session_state.current_audience = client_profile.get("Current_Target_Audience", "")
        if "ideal_audience" not in st.session_state:
            st.session_state.ideal_audience = client_profile.get("Ideal_Target_Audience", "")
        if "brand_values" not in st.session_state:
            st.session_state.brand_values = research_tools_framework.format_list_for_display(client_profile.get("Brand_Values", ""))
        if "brand_mission" not in st.session_state:
            st.session_state.brand_mission = client_profile.get("Brand_Mission", "")
        if "emotional_impact" not in st.session_state:
            st.session_state.emotional_impact = research_tools_framework.format_list_for_display(client_profile.get("Desired_Emotional_Impact", ""))
        if "brand_personality" not in st.session_state:
            st.session_state.brand_personality = research_tools_framework.format_list_for_display(client_profile.get("Brand_Personality", ""))
        if "avoid_topics" not in st.session_state:
            st.session_state.avoid_topics = client_profile.get("Words_Tones_To_Avoid", "")
        if "website_url" not in st.session_state:
            st.session_state.website_url = ""
        
        # Research section
        st.subheader("Research Options")
        
        # Website URL input
        website_url = st.text_input(
            "Client Website URL (optional)", 
            value=st.session_state.website_url,
            help="Enter the URL to the client's website to extract information automatically"
        )
        
        # Update session state with the website URL
        if website_url != st.session_state.website_url:
            st.session_state.website_url = website_url
        
        # Research buttons row
        research_col1, research_col2 = st.columns([1, 1])
        with research_col1:
            research_button = st.button("🔍 Research Missing Info", key="research_button", help="Use AI to research and fill in missing information")
        with research_col2:
            if website_url:
                extract_button = st.button("📄 Extract Website Content", key="extract_button", help="Extract content from the provided website URL")
            else:
                extract_button = False
        
        # Process extract button
        if extract_button and website_url:
            with st.spinner(f"Extracting content from {website_url}..."):
                extracted_content = extract_content_from_url(website_url)
                if extracted_content and not extracted_content.startswith("Error"):
                    st.success("✅ Content extracted from website!")
                    
                    # Show a sample of the extracted content
                    with st.expander("Preview extracted content"):
                        st.text_area("Website Content Sample", value=extracted_content[:1000] + "...", height=200, disabled=True)
                    
                    # Process the extracted content with AI
                    with st.spinner("Analyzing website content..."):
                        prompt = f"""Analyze the following content extracted from {selected_client}'s website and extract key information about:
1. What products or services they offer
2. Their target audience
3. Their brand values and mission
4. Their brand personality and tone

Website content:
{extracted_content[:5000]}

Return the extracted information as a JSON object with these fields:
- product_service_description
- current_target_audience
- brand_values
- brand_mission
- brand_personality
"""
                        
                        schema = {
                            "type": "object",
                            "properties": {
                                "product_service_description": {"type": "string"},
                                "current_target_audience": {"type": "string"},
                                "brand_values": {"type": "string"},
                                "brand_mission": {"type": "string"},
                                "brand_personality": {"type": "string"}
                            }
                        }
                        
                        response = universal_framework.call_gemini_api(prompt, response_schema=schema)
                        
                        try:
                            extracted_data = json.loads(response)
                            
                            # Update session state with extracted data (only for empty fields)
                            if not st.session_state.product_service and "product_service_description" in extracted_data:
                                st.session_state.product_service = extracted_data["product_service_description"]
                            if not st.session_state.current_audience and "current_target_audience" in extracted_data:
                                st.session_state.current_audience = extracted_data["current_target_audience"]
                            if not st.session_state.brand_values and "brand_values" in extracted_data:
                                st.session_state.brand_values = extracted_data["brand_values"]
                            if not st.session_state.brand_mission and "brand_mission" in extracted_data:
                                st.session_state.brand_mission = extracted_data["brand_mission"]
                            if not st.session_state.brand_personality and "brand_personality" in extracted_data:
                                st.session_state.brand_personality = extracted_data["brand_personality"]
                            
                            st.info("Website content analyzed and form fields updated. Please review and edit as needed.")
                            st.experimental_rerun()
                        except:
                            st.warning("Could not extract structured data from the website content. Please fill in the information manually.")
                else:
                    st.error(f"Failed to extract content from the website: {extracted_content}")
        
        # Process research button
        if research_button:
            # Collect minimal information we already have
            minimal_info = ""
            if st.session_state.product_service:
                minimal_info += f"Product/Service: {st.session_state.product_service}\n"
            if st.session_state.current_audience:
                minimal_info += f"Current Audience: {st.session_state.current_audience}\n"
            if st.session_state.brand_values:
                minimal_info += f"Brand Values: {st.session_state.brand_values}\n"
            
            # Research missing information
            researched_data = research_missing_information(
                selected_client,
                client_profile.get("Industry", ""),
                website_url if website_url else None,
                minimal_info
            )
            
            # Update session state with researched data for empty fields
            if not st.session_state.product_service and "product_service_description" in researched_data:
                st.session_state.product_service = researched_data["product_service_description"]
            if not st.session_state.current_audience and "current_target_audience" in researched_data:
                st.session_state.current_audience = researched_data["current_target_audience"]
            if not st.session_state.ideal_audience and "ideal_target_audience" in researched_data:
                st.session_state.ideal_audience = researched_data["ideal_target_audience"]
            if not st.session_state.brand_values and "brand_values" in researched_data:
                st.session_state.brand_values = researched_data["brand_values"]
            if not st.session_state.brand_mission and "brand_mission" in researched_data:
                st.session_state.brand_mission = researched_data["brand_mission"]
            if not st.session_state.emotional_impact and "desired_emotional_impact" in researched_data:
                st.session_state.emotional_impact = researched_data["desired_emotional_impact"]
            if not st.session_state.brand_personality and "brand_personality" in researched_data:
                st.session_state.brand_personality = researched_data["brand_personality"]
            if not st.session_state.avoid_topics and "words_tones_to_avoid" in researched_data:
                st.session_state.avoid_topics = researched_data["words_tones_to_avoid"]
            
            # Show success message
            st.success("✅ Missing information researched! Please review and edit as needed.")
            st.experimental_rerun()
        
        # Form for client information
        with st.form("context_form"):
            st.subheader("Client Information")
            
            # Name and Industry are read-only as they come from the main client profile
            st.text_input("Business Name", value=client_profile.get("Name", ""), disabled=True)
            st.text_input("Industry", value=client_profile.get("Industry", ""), disabled=True)
            
            # Editable fields using session state
            product_service = st.text_area(
                "Product/Service Description", 
                value=st.session_state.product_service,
                help="Describe what the client offers in 1-3 sentences."
            )
            
            current_audience = st.text_area(
                "Current Target Audience", 
                value=st.session_state.current_audience,
                help="Who does the client currently reach? Include demographics, interests, and pain points."
            )
            
            ideal_audience = st.text_area(
                "Ideal Target Audience", 
                value=st.session_state.ideal_audience,
                help="Who would the client ideally like to reach? May differ from current audience."
            )
            
            brand_values = st.text_input(
                "Brand Values (comma-separated)", 
                value=st.session_state.brand_values,
                help="Core principles that guide the brand (e.g., Innovation, Sustainability, Community)"
            )
            
            brand_mission = st.text_area(
                "Brand Mission", 
                value=st.session_state.brand_mission,
                help="The brand's purpose or reason for existing."
            )
            
            emotional_impact = st.text_input(
                "Desired Emotional Impact (comma-separated)", 
                value=st.session_state.emotional_impact,
                help="How should audience feel after engaging with the brand? (e.g., Inspired, Confident, Relieved)"
            )
            
            brand_personality = st.text_input(
                "Brand Personality (comma-separated)", 
                value=st.session_state.brand_personality,
                help="3-5 adjectives that describe the brand as if it were a person"
            )
            
            avoid_topics = st.text_area(
                "Words/Tones/Topics to Avoid", 
                value=st.session_state.avoid_topics,
                help="Language, topics, or approaches the brand wishes to stay away from"
            )
            
            # Update session state with form values
            if product_service != st.session_state.product_service:
                st.session_state.product_service = product_service
            if current_audience != st.session_state.current_audience:
                st.session_state.current_audience = current_audience
            if ideal_audience != st.session_state.ideal_audience:
                st.session_state.ideal_audience = ideal_audience
            if brand_values != st.session_state.brand_values:
                st.session_state.brand_values = brand_values
            if brand_mission != st.session_state.brand_mission:
                st.session_state.brand_mission = brand_mission
            if emotional_impact != st.session_state.emotional_impact:
                st.session_state.emotional_impact = emotional_impact
            if brand_personality != st.session_state.brand_personality:
                st.session_state.brand_personality = brand_personality
            if avoid_topics != st.session_state.avoid_topics:
                st.session_state.avoid_topics = avoid_topics
            
            # Advanced options expander
            with st.expander("Advanced Options"):
                optimize_content = st.checkbox("Optimize content for next steps", value=True,
                                             help="Rewrite content to make it more useful for brand voice development")
                
                # Removed model selection - using Gemini by default
            
            # Style the submit button
            st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 0.5em 1em;
            }
            </style>
            """, unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("Generate Context Summary")
        
        if submit_button:
            # Collect all form data
            form_data = {
                "product_service_description": product_service,
                "current_target_audience": current_audience,
                "ideal_target_audience": ideal_audience,
                "brand_values": brand_values,
                "brand_mission": brand_mission,
                "desired_emotional_impact": emotional_impact,
                "brand_personality": brand_personality,
                "words_tones_to_avoid": avoid_topics
            }
            
            # Optimize content if the option is selected
            if optimize_content:
                with st.spinner("Optimizing content..."):
                    optimized_data = optimize_content_for_next_steps(form_data)
                    
                    # Update form data with optimized content
                    form_data = optimized_data
            
            # Show progress
            with st.spinner("Generating context summary..."):
                # Construct prompt using template
                prompt = f"""Analyze and organize the following client information into a structured format. 
Extract key details about {selected_client} as reference material for brand voice research.

Here is the information provided:
- Business Name: {selected_client}
- Industry: {client_profile.get("Industry", "")}
- Product/Service Description: {form_data['product_service_description']}
- Current Target Audience: {form_data['current_target_audience']}
- Ideal Target Audience: {form_data['ideal_target_audience']}
- Brand Values: {form_data['brand_values']}
- Brand Mission: {form_data['brand_mission']}
- Desired Emotional Impact on Audience: {form_data['desired_emotional_impact']}
- Brand Personality: {form_data['brand_personality']}
- Words/Tones/Topics to Avoid: {form_data['words_tones_to_avoid']}

Provide a clear, concise summary for each field. If information for a field is missing or unclear, make your best assessment based on the available information.
"""
                
                # Use Gemini with fixed schema (without propertyOrdering)
                schema = get_fixed_context_gatherer_schema()
                response = universal_framework.call_gemini_api(prompt, response_schema=schema)
                
                try:
                    # Parse the JSON response
                    parsed_data = json.loads(response)
                    
                    # Define our own property order
                    property_order = [
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
                    
                    # Create a markdown table for display
                    md_table = "| Field | Value |\n|-------|-------|\n"
                    
                    for key in property_order:
                        if key in parsed_data:
                            # Convert key from snake_case to Title Case for display
                            display_key = " ".join(word.capitalize() for word in key.split("_"))
                            md_table += f"| {display_key} | {parsed_data.get(key, '')} |\n"
                    
                    # Display formatted table
                    st.subheader("Context Summary")
                    st.markdown(md_table)
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse structured response from Gemini")
                    st.text(response)  # Show raw response for debugging
                    return
                
                # Update Notion database
                # Map the parsed data to the database property names
                notion_data = {}
                
                # Mapping from JSON keys to Notion property names
                key_mapping = {
                    "business_name": "Name",
                    "industry": "Industry",
                    "product_service_description": "Product_Service_Description",
                    "current_target_audience": "Current_Target_Audience",
                    "ideal_target_audience": "Ideal_Target_Audience",
                    "brand_values": "Brand_Values",
                    "brand_mission": "Brand_Mission",
                    "desired_emotional_impact": "Desired_Emotional_Impact",
                    "brand_personality": "Brand_Personality",
                    "words_tones_to_avoid": "Words_Tones_To_Avoid"
                }
                
                # Map the parsed data to Notion property names
                for json_key, notion_key in key_mapping.items():
                    if json_key in parsed_data:
                        notion_data[notion_key] = parsed_data[json_key]
                
                # Update client profile in Notion
                success = db_manager.update_client_profile(client_page_id, notion_data)
                
                if success:
                    # Mark tool as complete
                    db_manager.mark_tool_complete(client_page_id, "context_gatherer")
                    st.success("✅ Client profile updated in Notion database")
                    
                    # Show next steps
                    st.info("**Next step:** Use the Content Collector tool to gather content samples across channels.")
                else:
                    st.error("Failed to update client profile in Notion database")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your Notion database is properly set up and refresh the page.")

def parse_context_output(response):
    """Parse Context Gatherer output from GPT-4"""
    parsed_data = {}
    
    # Use the shared function to parse markdown tables
    table_data = research_tools_framework.parse_markdown_table(response)
    
    if not table_data:
        return parsed_data
    
    # Map the table fields to the correct database properties
    field_mapping = {
        "Business Name": "business_name",
        "Industry": "industry",
        "Product/Service Description": "product_service_description",
        "Current Target Audience": "current_target_audience",
        "Ideal Target Audience": "ideal_target_audience",
        "Brand Values": "brand_values",
        "Brand Mission": "brand_mission",
        "Desired Emotional Impact on Audience": "desired_emotional_impact",
        "Brand Personality": "brand_personality",
        "Words/Tones/Topics to Avoid": "words_tones_to_avoid"
    }
    
    # Extract data from table
    for row in table_data:
        if "Field" in row and "Value" in row:
            field = row["Field"]
            value = row["Value"]
            
            if field in field_mapping and value:
                parsed_data[field_mapping[field]] = value
    
    return parsed_data


if __name__ == "__main__":
    run_context_gatherer()