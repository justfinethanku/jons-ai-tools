"""
Step 2: Brand Analyzer Tool

Comprehensive brand voice analysis using enhanced methodology.
Builds on website data from Step 1 and optionally form data to create
deep brand voice insights.

Can be run independently for testing:
    python -m tools.brand_builder.step_02_brand_analyzer --input step1_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework, research_tools_framework
from frameworks.prompt_wrappers import prompt_wrapper


def robust_json_parse(response_text):
    """
    Robust JSON parsing with multiple fallback strategies
    
    Args:
        response_text: The raw response text from API
        
    Returns:
        tuple: (success: bool, data: dict, error_msg: str)
    """
    # Strategy 1: Direct parsing after basic cleanup
    try:
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result_data = json.loads(clean_response)
        return True, result_data, None
        
    except json.JSONDecodeError:
        pass  # Continue to Strategy 2
    
    # Strategy 2: Extract content between first { and last }
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            return False, {}, f"No valid JSON brackets found in response: {response_text[:200]}..."
            
        json_text = response_text[start_idx:end_idx+1]
        result_data = json.loads(json_text)
        return True, result_data, None
        
    except json.JSONDecodeError:
        pass  # Continue to Strategy 3
    
    # Strategy 3: Try research_tools_framework.clean_json_response
    try:
        cleaned = research_tools_framework.clean_json_response(response_text)
        result_data = json.loads(cleaned)
        return True, result_data, None
        
    except:
        pass  # Continue to final fallback
    
    # Final fallback: Return detailed error
    return False, {}, f"All JSON parsing strategies failed. Response starts with: {response_text[:100]}... Response ends with: {response_text[-100:]}"


class BrandAnalyzerTool(WorkflowStep):
    """
    Step 2: Comprehensive brand voice analysis using enhanced methodology
    """
    
    def get_required_inputs(self):
        return ['client_name']  # Can work with minimal data
    
    def get_dependencies(self):
        return ['step_01_website_extractor']  # Prefers website data but not required
    
    def get_output_fields(self):
        return [
            'current_target_audience', 'ideal_target_audience', 'brand_values',
            'brand_mission', 'value_proposition', 'brand_personality_traits',
            'communication_tone', 'voice_characteristics', 'language_level',
            'desired_emotional_impact', 'brand_archetypes', 'competitive_differentiation',
            'content_themes', 'words_tones_to_avoid', 'messaging_priorities'
        ]
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute brand voice analysis"""
        client_name = context.get('client_name')
        
        # Get website data from Step 1 if available
        website_data = {}
        for field in ['industry', 'company_description', 'key_products_services', 
                     'target_markets', 'geographical_presence', 'company_size_indicators']:
            if context.get(field):
                website_data[field] = context.get(field)
        
        # Get form data if available
        form_data = {}
        for field in ['product_service_description', 'current_target_audience', 'ideal_target_audience',
                     'brand_values', 'brand_mission', 'desired_emotional_impact', 
                     'brand_personality', 'words_tones_to_avoid']:
            if context.get(field):
                form_data[field] = context.get(field)
        
        try:
            # Build rich input from website data
            website_context = f"""
**COMPANY OVERVIEW:**
- Name: {client_name}
- Industry: {website_data.get('industry', 'Unknown')}
- Description: {website_data.get('company_description', 'Not available')}
- Products/Services: {', '.join(website_data.get('key_products_services', []))}
- Target Markets: {', '.join(website_data.get('target_markets', []))}
- Geographical Presence: {website_data.get('geographical_presence', 'Not specified')}
- Company Size Indicators: {website_data.get('company_size_indicators', 'Not specified')}"""
            
            # Get prompt and temperature from modular system
            prompt, temperature = prompt_wrapper.get_brand_voice_analysis_prompt(
                client_name=client_name,
                website_data=website_data,
                form_data=form_data
            )
            
            # Define API schema for brand voice analysis validation
            api_schema = {
                "type": "object",
                "properties": {
                    "current_target_audience": {"type": "string"},
                    "ideal_target_audience": {"type": "string"},
                    "brand_values": {"type": "array", "items": {"type": "string"}},
                    "brand_mission": {"type": "string"},
                    "value_proposition": {"type": "string"},
                    "brand_personality_traits": {"type": "array", "items": {"type": "string"}},
                    "communication_tone": {"type": "string"},
                    "voice_characteristics": {"type": "array", "items": {"type": "string"}},
                    "language_level": {"type": "string"},
                    "desired_emotional_impact": {"type": "array", "items": {"type": "string"}},
                    "brand_archetypes": {"type": "array", "items": {"type": "string"}},
                    "competitive_differentiation": {"type": "string"},
                    "content_themes": {"type": "array", "items": {"type": "string"}},
                    "words_tones_to_avoid": {"type": "array", "items": {"type": "string"}},
                    "messaging_priorities": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["current_target_audience", "ideal_target_audience", "brand_values", "brand_mission", "brand_personality_traits"]
            }
            
            # Call API
            response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
            
            # Check for API error responses before JSON parsing
            if response.startswith("Error:"):
                return StepResult(
                    success=False,
                    data={},
                    errors=[f"API call failed: {response}"],
                    warnings=[],
                    step_name=self.name
                )
            
            # Use robust JSON parsing with multiple fallback strategies
            parse_success, result_data, parse_error = robust_json_parse(response)
            if not parse_success:
                return StepResult(
                    success=False,
                    data={},
                    errors=[parse_error],
                    warnings=[],
                    step_name=self.name
                )
            
            # Combine with website data if available
            final_data = {**website_data, **result_data}
            
            return StepResult(
                success=True,
                data=final_data,
                errors=[],
                warnings=[],
                step_name=self.name
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                data={},
                errors=[f"Brand voice analysis failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze brand voice for Brand Builder')
    parser.add_argument('--client', required=True, help='Client name')
    parser.add_argument('--input', help='Input JSON file from previous step')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    # Create context
    context_data = {'client_name': args.client}
    
    # Load input data if provided
    if args.input:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
            context_data.update(input_data)
    
    context = WorkflowContext(context_data)
    
    # Run step
    step = BrandAnalyzerTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Brand analysis successful!")
        print(f"📊 Generated {len(result.data)} brand insights")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
        else:
            print("📋 Key Results:")
            key_fields = ['brand_mission', 'brand_values', 'current_target_audience', 'brand_personality_traits']
            for field in key_fields:
                if field in result.data:
                    print(f"  {field}: {result.data[field]}")
    else:
        print("❌ Brand analysis failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()