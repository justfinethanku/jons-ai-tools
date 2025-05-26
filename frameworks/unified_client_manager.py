"""
unified_client_manager 
Unified Client Management System

This module provides a centralized, consistent client selection interface
for all tools across the AI Tools project. It resolves conflicts between
different client selection patterns and provides state isolation.

Key Features:
- Single client selection interface
- Session state isolation
- Automatic cleanup mechanisms
- Consistent database integration
- Error recovery and fallback handling
"""

import streamlit as st
from typing import Optional, Tuple, Dict, Any
from frameworks.database_manager import NotionDatabaseManager
from frameworks.logging_manager import get_logger


class UnifiedClientManager:
    """Centralized client management with state isolation"""
    
    def __init__(self, tool_name: str = "default"):
        self.tool_name = tool_name
        self.session_key = f"ucm_{tool_name}"
        self._db_manager = None
        self.logger = get_logger(f"client_manager_{tool_name}")
    
    @property
    def db_manager(self) -> NotionDatabaseManager:
        """Lazy-load database manager with error handling"""
        if self._db_manager is None:
            try:
                self._db_manager = NotionDatabaseManager()
            except Exception as e:
                self.logger.error("Configuration required", error=str(e))
                st.error(f"🔧 **Configuration Required**: {str(e)}")
                st.error("Please configure your Notion API credentials.")
                st.stop()
        return self._db_manager
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get isolated session state for this tool"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                'client_page_id': None,
                'client_name': None,
                'client_profile': {},
                'tool_status': {},
                'last_updated': None
            }
        
        # Safety check: ensure we have a dictionary, not a corrupted object
        session_data = st.session_state[self.session_key]
        if not isinstance(session_data, dict):
            # Corrupted session state - recreate it
            st.session_state[self.session_key] = {
                'client_page_id': None,
                'client_name': None,
                'client_profile': {},
                'tool_status': {},
                'last_updated': None
            }
            session_data = st.session_state[self.session_key]
        
        return session_data
    
    def clear_session_state(self):
        """Clear session state for this tool"""
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
    
    @staticmethod
    def cleanup_all_sessions():
        """Clean up all unified client manager sessions"""
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('ucm_')]
        for key in keys_to_remove:
            del st.session_state[key]
    
    @staticmethod
    def cleanup_stale_sessions(max_age_minutes: int = 60):
        """Clean up sessions older than max_age_minutes"""
        import datetime
        current_time = datetime.datetime.now()
        
        keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith('ucm_') and isinstance(st.session_state[key], dict):
                session_data = st.session_state[key]
                last_updated = session_data.get('last_updated')
                if last_updated:
                    try:
                        last_update_time = datetime.datetime.fromisoformat(last_updated)
                        if (current_time - last_update_time).total_seconds() > (max_age_minutes * 60):
                            keys_to_remove.append(key)
                    except (ValueError, TypeError):
                        # Invalid timestamp, mark for removal
                        keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
    
    def update_session_timestamp(self):
        """Update the last_updated timestamp for this session"""
        import datetime
        session_state = self.get_session_state()
        session_state['last_updated'] = datetime.datetime.now().isoformat()
    
    def client_selector_sidebar(self, allow_new_client: bool = True) -> Tuple[Optional[str], Optional[str], Dict[str, bool]]:
        """
        Unified client selector with consistent interface
        
        Args:
            allow_new_client: Whether to allow creating new clients
            
        Returns:
            Tuple of (client_page_id, client_name, tool_status)
        """
        st.sidebar.title(f"🎯 Client Selection - {self.tool_name.title()}")
        
        try:
            # Get client list
            client_list = self.db_manager.get_client_list()
            client_options = list(client_list.keys())
            
            # Add "Create New Client" option if allowed
            if allow_new_client:
                client_options = ["➕ Create New Client"] + client_options
            
            # Handle empty client list
            if not client_options and not allow_new_client:
                st.sidebar.warning("No clients found in Notion database.")
                st.sidebar.info("Please add clients directly in Notion or allow client creation.")
                return None, None, {}
            
            # Client selection dropdown
            selected_client = st.sidebar.selectbox(
                "Select Client",
                options=client_options,
                key=f"{self.session_key}_selector",
                help="Choose an existing client or create a new one"
            )
            
            # Handle new client creation
            if selected_client == "➕ Create New Client":
                return self._handle_new_client_creation()
            
            # Handle existing client selection
            elif selected_client and selected_client in client_list:
                return self._handle_existing_client_selection(selected_client, client_list)
            
            else:
                st.sidebar.info("Please select a client to get started.")
                return None, None, {}
                
        except Exception as e:
            st.sidebar.error(f"❌ Client management error: {str(e)}")
            return None, None, {}
    
    def _handle_new_client_creation(self) -> Tuple[Optional[str], Optional[str], Dict[str, bool]]:
        """Handle new client creation workflow"""
        with st.sidebar.form(f"{self.session_key}_new_client_form"):
            st.subheader("Create New Client")
            new_client_name = st.text_input("Client Name", key=f"{self.session_key}_new_name")
            website_url = st.text_input(
                "Website URL (optional)", 
                key=f"{self.session_key}_new_website",
                help="Provide URL to auto-extract company information"
            )
            
            create_button = st.form_submit_button("Create Client")
            
            if create_button and new_client_name:
                return self._create_new_client(new_client_name, website_url)
        
        return None, None, {}
    
    def _create_new_client(self, client_name: str, website_url: str) -> Tuple[Optional[str], Optional[str], Dict[str, bool]]:
        """Create new client with optional website analysis"""
        try:
            # Handle website analysis if URL provided
            extracted_data = None
            if website_url.strip():
                extracted_data = self._analyze_website(client_name, website_url.strip())
            
            # Determine industry
            new_client_industry = "Other"
            if extracted_data:
                new_client_industry = extracted_data.get("industry", "Other")
            
            # Create the client
            new_client_id = self.db_manager.create_new_client(client_name, new_client_industry)
            
            if not new_client_id:
                st.sidebar.error("Failed to create new client")
                return None, None, {}
            
            # Update with extracted data if available
            if extracted_data:
                self._update_client_with_extracted_data(new_client_id, extracted_data, website_url)
            elif website_url.strip():
                self.db_manager.update_client_profile(new_client_id, {"Website": website_url.strip()})
            
            # Update session state
            session_state = self.get_session_state()
            session_state['client_page_id'] = new_client_id
            session_state['client_name'] = client_name
            session_state['client_profile'] = extracted_data or {}
            self.update_session_timestamp()
            
            self.logger.log_operation_success("create_client", client_id=new_client_id, client_name=client_name)
            st.sidebar.success(f"✅ Created new client: {client_name}")
            
            return new_client_id, client_name, self._get_default_tool_status()
            
        except Exception as e:
            self.logger.log_operation_failure("create_client", str(e), client_name=client_name)
            st.sidebar.error(f"Failed to create client: {str(e)}")
            return None, None, {}
    
    def _analyze_website(self, client_name: str, website_url: str) -> Optional[Dict[str, Any]]:
        """Analyze website and extract company data"""
        try:
            from tools.brand_builder import extract_website_data, analyze_brand_voice
            
            # Step 1: Extract website data
            with st.spinner("Step 1: Extracting company data from website..."):
                step1_success, website_data, step1_error = extract_website_data(client_name, website_url)
            
            if not step1_success:
                st.sidebar.error(f"Step 1 failed: {step1_error}")
                return None
            
            st.sidebar.success("✅ Step 1 complete: Company data extracted")
            
            # Step 2: Analyze brand voice
            with st.spinner("Step 2: Analyzing brand voice..."):
                step2_success, analysis_result, step2_error = analyze_brand_voice(client_name, website_data)
            
            if step2_success:
                st.sidebar.success("✅ Step 2 complete: Brand voice analysis finished")
                return analysis_result
            else:
                st.sidebar.warning(f"Step 2 partial: {step2_error}")
                return website_data  # Use partial data
                
        except Exception as e:
            self.logger.error("Website analysis failed", error=str(e), client_name=client_name, website_url=website_url)
            st.sidebar.error(f"Website analysis failed: {str(e)}")
            return None
    
    def _update_client_with_extracted_data(self, client_id: str, extracted_data: Dict[str, Any], website_url: str):
        """Update client profile with extracted website data"""
        notion_data = {
            "Industry": extracted_data.get("industry", "Other"),
            "Website": website_url,
            "Product_Service_Description": extracted_data.get("product_service_description", ""),
            "Current_Target_Audience": extracted_data.get("current_target_audience", ""),
            "Ideal_Target_Audience": extracted_data.get("ideal_target_audience", ""),
            "Brand_Values": self._format_list_field(extracted_data.get("brand_values", "")),
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
            "Other_Social_Media": self._format_list_field(extracted_data.get("other_social_media", ""))
        }
        
        self.db_manager.update_client_profile(client_id, notion_data)
    
    def _handle_existing_client_selection(self, selected_client: str, client_list: Dict[str, str]) -> Tuple[str, str, Dict[str, bool]]:
        """Handle selection of existing client"""
        client_page_id = client_list[selected_client]
        
        # Update session state
        session_state = self.get_session_state()
        session_state['client_page_id'] = client_page_id
        session_state['client_name'] = selected_client
        self.update_session_timestamp()
        
        # Get client profile and tool status
        client_profile = self.db_manager.get_client_profile(client_page_id)
        session_state['client_profile'] = client_profile
        
        try:
            tool_status = self.db_manager.get_tool_completion_status(client_page_id)
            session_state['tool_status'] = tool_status
            
            # Display progress
            self._display_tool_progress(tool_status)
            
        except Exception:
            st.sidebar.warning("Could not retrieve tool status.")
            tool_status = self._get_default_tool_status()
        
        return client_page_id, selected_client, tool_status
    
    def _display_tool_progress(self, status: Dict[str, bool]):
        """Display tool completion progress in sidebar"""
        st.sidebar.markdown("### Research Progress")
        status_emojis = {True: "✅", False: "⬜"}
        
        tool_labels = [
            ("brand_builder", "1. Brand Builder"),
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
    
    def _format_list_field(self, field_value) -> str:
        """Format list fields for database storage"""
        if isinstance(field_value, list):
            return ", ".join(field_value)
        return str(field_value) if field_value else ""
    
    def _get_default_tool_status(self) -> Dict[str, bool]:
        """Get default tool status (all incomplete)"""
        return {
            "brand_builder": False,
            "content_collector": False,
            "voice_auditor": False,
            "audience_definer": False,
            "voice_traits_builder": False,
            "gap_analyzer": False,
            "content_rewriter": False,
            "guidelines_finalizer": False
        }
    
    def get_current_client(self) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """Get currently selected client info"""
        session_state = self.get_session_state()
        return (
            session_state.get('client_page_id'),
            session_state.get('client_name'),
            session_state.get('client_profile', {})
        )
    
    def mark_tool_complete(self, tool_name: str) -> bool:
        """Mark a tool as complete for the current client"""
        client_page_id, _, _ = self.get_current_client()
        if client_page_id:
            return self.db_manager.mark_tool_complete(client_page_id, tool_name)
        return False


def get_unified_client_manager(tool_name: str) -> UnifiedClientManager:
    """Factory function to get unified client manager for a tool"""
    session_key = f"ucm_{tool_name}"
    
    # Check if we have a valid manager
    if session_key in st.session_state:
        manager = st.session_state[session_key]
        if isinstance(manager, UnifiedClientManager):
            return manager
        else:
            # Clear corrupted entry
            del st.session_state[session_key]
    
    # Create new manager
    st.session_state[session_key] = UnifiedClientManager(tool_name)
    return st.session_state[session_key]


# Backward compatibility functions
def client_selector_sidebar(db_manager=None, allow_new_client=False, tool_name="legacy"):
    """Backward compatibility wrapper for existing code"""
    # db_manager parameter kept for compatibility but not used
    manager = get_unified_client_manager(tool_name)
    return manager.client_selector_sidebar(allow_new_client)


def client_selection_sidebar(tool_name="universal"):
    """Backward compatibility for universal_framework"""
    manager = get_unified_client_manager(tool_name)
    client_page_id, client_name, _ = manager.client_selector_sidebar(allow_new_client=False)
    
    # Store in global session state for backward compatibility
    if client_page_id:
        client_profile = manager.get_session_state().get('client_profile', {})
        # Ensure client_profile is a dictionary
        if not isinstance(client_profile, dict):
            client_profile = {}
        
        st.session_state["selected_client"] = {
            'id': client_page_id,
            'name': client_name,
            **client_profile
        }
    else:
        st.session_state["selected_client"] = None