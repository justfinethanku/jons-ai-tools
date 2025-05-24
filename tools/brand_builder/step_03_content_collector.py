"""
Step 3: Content Collector Tool

Identifies and catalogs brand communications across channels.
This step builds content strategy recommendations based on brand insights.

Can be run independently for testing:
    python -m tools.brand_builder.step_03_content_collector --input step2_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class ContentCollectorTool(WorkflowStep):
    """
    Step 3: Content Collector - Identifies and catalogs brand communications across channels
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_02_brand_analyzer']
    
    def get_output_fields(self):
        return ['content_samples']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute content collection"""
        client_name = context.get('client_name')
        
        # Build context from brand data
        brand_context = f"""
**BRAND OVERVIEW:**
- Company: {client_name}
- Industry: {context.get('industry', 'Unknown')}
- Description: {context.get('product_service_description', context.get('company_description', ''))}
- Mission: {context.get('brand_mission', 'Not specified')}
- Values: {context.get('brand_values', 'Not specified')}
- Target Audience: {context.get('ideal_target_audience', context.get('current_target_audience', 'Not specified'))}
- Brand Personality: {context.get('brand_personality', context.get('brand_personality_traits', 'Not specified'))}"""
        
        industry_context = f"Industry: {context.get('industry', 'General')} - Consider industry-specific communication channels and content types."
        
        try:
            # Get the prompt using the wrapper system
            prompt, temperature = prompt_wrapper.get_content_collection_prompt(
                brand_context=brand_context, 
                industry_context=industry_context,
                target_channels=None  # Let AI suggest optimal channels
            )
            
            # Define schema for API validation
            api_schema = {
                "type": "object",
                "properties": {
                    "content_samples": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "content_type": {"type": "string"},
                                "sample_description": {"type": "string"},
                                "strategic_notes": {"type": "string"}
                            },
                            "required": ["channel", "content_type", "sample_description", "strategic_notes"]
                        }
                    }
                },
                "required": ["content_samples"]
            }
            
            # Call the AI
            response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
            
            # Check for API error responses
            if response.startswith("Error:"):
                return StepResult(
                    success=False,
                    data={},
                    errors=[f"API call failed: {response}"],
                    warnings=[],
                    step_name=self.name
                )
            
            result_data = json.loads(response)
            
            return StepResult(
                success=True,
                data=result_data,
                errors=[],
                warnings=[],
                step_name=self.name
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                data={},
                errors=[f"Content collection failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect content strategy for Brand Builder')
    parser.add_argument('--client', required=True, help='Client name')
    parser.add_argument('--input', help='Input JSON file from previous steps')
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
    step = ContentCollectorTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Content collection successful!")
        print(f"📊 Generated {len(result.data.get('content_samples', []))} content recommendations")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
        else:
            print("📋 Content Samples:")
            for sample in result.data.get('content_samples', [])[:3]:  # Show first 3
                print(f"  - {sample.get('channel')}: {sample.get('content_type')}")
    else:
        print("❌ Content collection failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()