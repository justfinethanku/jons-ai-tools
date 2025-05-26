"""
Step 2: Brand Analyzer Tool - FULLY AUTOMATED
Analyzes brand voice and personality based on website data from Step 1
NO USER INPUT REQUIRED - Runs automatically after Step 1
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from frameworks import universal_framework
from frameworks.database_manager import NotionDatabaseManager
from frameworks.logging_manager import get_logger, LoggedOperation
from frameworks.shared_utils import safe_json_parse
from prompts.research_prompts.step02_Prompts.brand_analysis import get_brand_analysis_prompt


# Base classes copied from step_01_website_extractor.py
class WorkflowContext:
    """Simple context for passing data between workflow steps"""
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
    
    def set_input(self, key, value):
        self.inputs[key] = value
    
    def get_input(self, key, default=None):
        return self.inputs.get(key, default)
    
    def set_output(self, key, value):
        self.outputs[key] = value
    
    def get_output(self, key, default=None):
        return self.outputs.get(key, default)


class StepResult:
    """Simple result object for workflow steps"""
    def __init__(self, success=False, data=None, errors=None, warnings=None, step_name=None):
        self.success = success
        self.data = data or {}
        self.errors = errors or []
        self.warnings = warnings or []
        self.step_name = step_name


class WorkflowStep:
    """Base class for workflow steps"""
    def execute(self, context: WorkflowContext) -> StepResult:
        raise NotImplementedError("Subclasses must implement execute method")


class BrandAnalyzer(WorkflowStep):
    """
    FULLY AUTOMATED brand analysis pipeline
    Input: client_id from Step 1 (via context outputs)
    Output: Comprehensive brand voice analysis
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("brand_analyzer")
        
        # Initialize database manager
        try:
            self.db_manager = NotionDatabaseManager()
            self.logger.log_operation_success("initialize_database_manager")
        except Exception as e:
            self.logger.log_operation_failure("initialize_database_manager", str(e))
            self.db_manager = None
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """
        Execute the brand analysis workflow
        FULLY AUTOMATED - NO USER INPUT
        """
        with LoggedOperation("brand_analysis_pipeline", logger=self.logger) as op:
            try:
                # CRITICAL: Get client_id from context OUTPUTS (where Step 1 put it)
                client_id = context.get_output("client_id")
                
                if not client_id:
                    error_msg = "No client_id found in context outputs"
                    self.logger.error(error_msg)
                    return StepResult(
                        success=False,
                        errors=[error_msg],
                        step_name="brand_analyzer"
                    )
                
                self.logger.info(f"Starting brand analysis for client_id: {client_id}")
                
                # Fetch ALL data from Notion
                self.logger.info("Fetching client profile from Notion")
                client_profile = self.db_manager.get_client_profile(client_id)
                
                if not client_profile:
                    error_msg = f"Could not fetch client profile for {client_id}"
                    self.logger.error(error_msg)
                    return StepResult(
                        success=False,
                        errors=[error_msg],
                        step_name="brand_analyzer"
                    )
                
                # Extract all the website data that Step 1 saved
                client_name = client_profile.get("Name", "Unknown Client")
                self.logger.info(f"Analyzing brand for: {client_name}")
                
                # Build comprehensive view of all available data
                website_data = {
                    "Industry": client_profile.get("Industry", ""),
                    "Company_Description": client_profile.get("Company_Description", ""),
                    "Brand_Mission": client_profile.get("Brand_Mission", ""),
                    "Brand_Values": client_profile.get("Brand_Values", ""),
                    "Value_Proposition": client_profile.get("Value_Proposition", ""),
                    "Brand_Personality": client_profile.get("Brand_Personality", ""),
                    "Product_Service_Description": client_profile.get("Product_Service_Description", ""),
                    "Target_Audience": client_profile.get("Target_Audience", ""),
                    "Communication_Tone": client_profile.get("Communication_Tone", ""),
                    "Desired_Emotional_Impact": client_profile.get("Desired_Emotional_Impact", ""),
                    "Website": client_profile.get("Website", ""),
                    "Company_Size": client_profile.get("Company_Size", ""),
                    "Contact_Email": client_profile.get("Contact_Email", ""),
                    "Phone_Number": client_profile.get("Phone_Number", ""),
                    "Location": client_profile.get("Location", ""),
                    "LinkedIn_URL": client_profile.get("LinkedIn_URL", ""),
                    "Twitter_URL": client_profile.get("Twitter_URL", ""),
                    "Facebook_URL": client_profile.get("Facebook_URL", ""),
                    "Instagram_URL": client_profile.get("Instagram_URL", ""),
                    "Other_Social_Media": client_profile.get("Other_Social_Media", ""),
                }
                
                # Get the Deep_Research_Workflow data that Step 1 stored
                deep_research_raw = client_profile.get("Deep_Research_Workflow", "{}")
                deep_research = safe_json_parse(deep_research_raw, {})
                website_extraction = deep_research.get("website_extraction", {})
                
                # Add website extraction data to our analysis
                if website_extraction:
                    website_data["key_messaging_themes"] = website_extraction.get("key_messaging_themes", {})
                    website_data["communication_patterns"] = website_extraction.get("communication_patterns", {})
                    website_data["brand_voice_indicators"] = website_extraction.get("brand_voice_indicators", {})
                
                # Build content summary from what we have
                content_summary = self._build_content_summary(client_name, website_data)
                
                # Get prompt and analyze
                self.logger.info("Generating brand analysis prompt")
                prompt = get_brand_analysis_prompt(client_name, website_data, content_summary)
                
                # Call AI for analysis
                self.logger.info("Calling AI for brand voice analysis")
                response = universal_framework.call_openai_api(
                    prompt,
                    model="gpt-4o-mini-2024-07-18"
                )
                
                if not response:
                    error_msg = "Failed to get AI response for brand analysis"
                    self.logger.error(error_msg)
                    return StepResult(
                        success=False,
                        errors=[error_msg],
                        step_name="brand_analyzer"
                    )
                
                # Parse the results
                parsed_results = safe_json_parse(response, {})
                if not parsed_results:
                    # If JSON parsing fails, store as text
                    parsed_results = {"raw_analysis": response}
                
                self.logger.info("Brand analysis completed successfully")
                
                # Save results back to Notion
                self._save_to_notion(client_id, client_profile, parsed_results)
                
                # CRITICAL: Set outputs for the next step
                context.set_output("client_id", client_id)  # Pass it forward
                context.set_output("brand_analysis", parsed_results)
                
                # TODO: Add handoff to Step 3 here when it exists
                # if self.db_manager:
                #     self.logger.info("Handing off to Step 3: Content Collector")
                #     from .step_03_content_collector import ContentCollector
                #     step3 = ContentCollector()
                #     step3_result = step3.execute(context)
                #     if not step3_result.success:
                #         self.logger.error(f"Step 3 failed: {step3_result.errors}")
                
                op.success = True
                return StepResult(
                    success=True,
                    data={
                        "client_id": client_id,
                        "brand_analysis": parsed_results
                    },
                    step_name="brand_analyzer"
                )
                
            except Exception as e:
                error_msg = f"Brand analysis pipeline failed: {str(e)}"
                self.logger.error(error_msg)
                import traceback
                traceback.print_exc()
                return StepResult(
                    success=False,
                    errors=[error_msg],
                    step_name="brand_analyzer"
                )
    
    def _build_content_summary(self, client_name, website_data):
        """Build a comprehensive content summary from all available data"""
        summary = f"Company: {client_name}\n\n"
        
        # Add non-empty fields to summary
        field_mappings = {
            "Industry": "Industry",
            "Company_Description": "Description",
            "Brand_Mission": "Mission",
            "Brand_Values": "Values",
            "Value_Proposition": "Value Proposition",
            "Brand_Personality": "Personality",
            "Product_Service_Description": "Products/Services",
            "Target_Audience": "Target Audience",
            "Communication_Tone": "Communication Tone",
            "Desired_Emotional_Impact": "Emotional Impact",
            "Company_Size": "Company Size",
            "Location": "Location"
        }
        
        for field, label in field_mappings.items():
            value = website_data.get(field)
            if value and value != "Not found" and value != "":
                summary += f"{label}: {value}\n"
        
        # Add social media if present
        social_urls = []
        for social in ["LinkedIn_URL", "Twitter_URL", "Facebook_URL", "Instagram_URL"]:
            url = website_data.get(social)
            if url and url != "Not found":
                social_urls.append(f"{social.replace('_URL', '')}: {url}")
        
        if social_urls:
            summary += f"\nSocial Media:\n" + "\n".join(social_urls) + "\n"
        
        # Add key messaging themes if available
        if website_data.get("key_messaging_themes"):
            summary += f"\nKey Messaging Themes: {json.dumps(website_data['key_messaging_themes'], indent=2)}\n"
        
        return summary
    
    def _save_to_notion(self, client_id, client_profile, parsed_results):
        """Save brand analysis results back to Notion"""
        try:
            self.logger.info("Saving brand analysis to Notion")
            
            # Get existing workflow data
            deep_research_raw = client_profile.get("Deep_Research_Workflow", "{}")
            workflow_data = safe_json_parse(deep_research_raw, {})
            
            # Add our analysis
            workflow_data["brand_analysis"] = {
                "analysis_results": parsed_results,
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            # Update Notion with the new analysis
            update_data = {
                "Deep_Research_Workflow": json.dumps(workflow_data),
                "Research_Status": "Brand Analysis Completed"
            }
            
            # Also update specific fields if they were analyzed
            if isinstance(parsed_results, dict):
                # Map analysis results to Notion fields
                if parsed_results.get("brand_voice"):
                    update_data["Communication_Tone"] = str(parsed_results["brand_voice"])
                
                if parsed_results.get("tone_characteristics"):
                    update_data["Brand_Personality"] = str(parsed_results["tone_characteristics"])
                
                if parsed_results.get("messaging_guidelines"):
                    # Store in a custom field or append to existing
                    existing_notes = client_profile.get("Notes", "")
                    new_notes = f"{existing_notes}\n\nBrand Messaging Guidelines:\n{parsed_results['messaging_guidelines']}"
                    update_data["Notes"] = new_notes.strip()
            
            # Save back to Notion
            success = self.db_manager.update_client_profile(client_id, update_data)
            
            if success:
                self.logger.info("Brand analysis saved to Notion successfully")
            else:
                self.logger.error("Failed to save brand analysis to Notion")
                
        except Exception as e:
            self.logger.error(f"Error saving to Notion: {str(e)}")
            import traceback
            traceback.print_exc()