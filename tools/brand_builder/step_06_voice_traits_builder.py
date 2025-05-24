"""
Step 6: Voice Traits Builder Tool

Builds actionable voice traits and characteristics based on audience and brand insights.

Can be run independently for testing:
    python -m tools.brand_builder.step_06_voice_traits_builder --input step5_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class VoiceTraitsBuilderTool(WorkflowStep):
    """
    Step 6: Voice Traits Builder - Builds actionable voice traits and characteristics
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_05_audience_definer']
    
    def get_output_fields(self):
        return ['voice_traits', 'actionable_guidelines', 'communication_framework']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute voice traits building"""
        client_name = context.get('client_name')
        
        try:
            # Build comprehensive context from all previous steps
            comprehensive_insights = {
                'brand_data': {
                    'mission': context.get('brand_mission'),
                    'values': context.get('brand_values'),
                    'personality': context.get('brand_personality_traits')
                },
                'audience_data': context.get('detailed_personas', {}),
                'voice_data': context.get('voice_audit_summary', {}),
                'content_data': context.get('content_samples', [])
            }
            
            brand_context = json.dumps(comprehensive_insights, indent=2)
            industry_context = f"Industry: {context.get('industry', 'General')}"
            
            # Get prompt using wrapper system  
            prompt, temperature = prompt_wrapper.get_voice_traits_builder_prompt(
                brand_context=brand_context,
                audience_insights=json.dumps(context.get('detailed_personas', {})),
                voice_audit_results=json.dumps(context.get('voice_audit_summary', {})),
                industry_context=industry_context
            )
            
            # Call API
            response = universal_framework.call_gemini_api(prompt, temperature=temperature)
            
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
                errors=[f"Voice traits building failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build voice traits for Brand Builder')
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
    step = VoiceTraitsBuilderTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Voice traits building successful!")
        print(f"📊 Analysis complete")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
    else:
        print("❌ Voice traits building failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()