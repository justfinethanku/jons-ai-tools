# notion_client_manager.py
import os
from notion_client import Client
import streamlit as st
from typing import Dict, List, Optional
import json

class NotionClientManager:
    def __init__(self):
        self.notion = None
        self.database_id = None
        self._initialize_notion()
    
    def _initialize_notion(self):
        """Initialize Notion client from Streamlit secrets or env vars"""
        try:
            # Try Streamlit secrets first
            api_key = st.secrets.get("NOTION_API_KEY")
            self.database_id = st.secrets.get("NOTION_DATABASE_ID")
            
            # Fall back to environment variables
            if not api_key:
                api_key = os.getenv("NOTION_API_KEY")
                self.database_id = os.getenv("NOTION_DATABASE_ID")
            
            if api_key:
                self.notion = Client(auth=api_key)
                st.success("✅ Notion connected successfully!")
            else:
                st.warning("⚠️ Notion not configured. Add API key to continue.")
                
        except Exception as e:
            st.error(f"Notion connection failed: {str(e)}")
    
    def get_clients(self) -> List[Dict]:
        """Fetch all clients from Notion database"""
        if not self.notion or not self.database_id:
            return []
        
        try:
            response = self.notion.databases.query(database_id=self.database_id)
            clients = []
            
            for page in response["results"]:
                client = self._format_client(page)
                if client:
                    clients.append(client)
            
            return clients
        except Exception as e:
            st.error(f"Failed to fetch clients: {str(e)}")
            return []
    
    def _format_client(self, page: Dict) -> Optional[Dict]:
        """Convert Notion page to client dict"""
        try:
            properties = page["properties"]
            
            # Extract client data (adjust field names to match your template)
            client = {
                "id": page["id"],
                "name": self._extract_title(properties.get("Name", {})),
                "brand_voice": self._extract_rich_text(properties.get("Brand Voice", {})),
                "custom_prompts": self._extract_rich_text(properties.get("Custom Prompts", {})),
                "tone": self._extract_select(properties.get("Tone", {})),
                "industry": self._extract_select(properties.get("Industry", {})),
                "target_audience": self._extract_rich_text(properties.get("Target Audience", {})),
                "keywords": self._extract_multi_select(properties.get("Keywords", {})),
                "created_time": page["created_time"],
                "last_edited_time": page["last_edited_time"]
            }
            return client
        except Exception as e:
            st.error(f"Error formatting client: {str(e)}")
            return None
    
    def _extract_title(self, prop: Dict) -> str:
        """Extract title from Notion property"""
        if "title" in prop and prop["title"]:
            return prop["title"][0]["plain_text"]
        return ""
    
    def _extract_rich_text(self, prop: Dict) -> str:
        """Extract rich text from Notion property"""
        if "rich_text" in prop and prop["rich_text"]:
            return " ".join([text["plain_text"] for text in prop["rich_text"]])
        return ""
    
    def _extract_select(self, prop: Dict) -> str:
        """Extract select value from Notion property"""
        if "select" in prop and prop["select"]:
            return prop["select"]["name"]
        return ""
    
    def _extract_multi_select(self, prop: Dict) -> List[str]:
        """Extract multi-select values from Notion property"""
        if "multi_select" in prop and prop["multi_select"]:
            return [option["name"] for option in prop["multi_select"]]
        return []
    
    def save_generated_content(self, client_id: str, content_type: str, content: str, platform: str = None):
        """Save generated content back to Notion"""
        if not self.notion:
            return
        
        try:
            # Create a new page in the AI Library or update existing client
            # This is optional - you might want to track generated content
            pass
        except Exception as e:
            st.error(f"Failed to save content: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Notion is properly connected"""
        return self.notion is not None and self.database_id is not None