"""
Step 9: Guidelines Finalizer Tool

Synthesizes all workflow insights into comprehensive Brand Voice Guidelines document.
This is the final step that produces the turnkey guidelines.

Can be run independently for testing:
    python -m tools.brand_builder.step_09_guidelines_finalizer --input step8_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class GuidelinesFinalizerTool(WorkflowStep):
    """
    Step 9: Guidelines Finalizer - Synthesizes all insights into comprehensive Brand Voice Guidelines
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_08_content_rewriter']
    
    def get_output_fields(self):
        return ['brand_voice_guidelines', 'implementation_roadmap', 'final_document']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute guidelines finalization"""
        client_name = context.get('client_name')
        
        try:
            # Synthesize ALL insights from the complete workflow
            comprehensive_insights = {
                'brand_foundation': {
                    'mission': context.get('brand_mission'),
                    'values': context.get('brand_values'),
                    'personality': context.get('brand_personality_traits'),
                    'positioning': context.get('competitive_differentiation')
                },
                'audience_insights': context.get('detailed_personas', {}),
                'voice_framework': context.get('voice_traits', {}),
                'content_strategy': context.get('content_samples', []),
                'competitive_intelligence': context.get('strategic_gaps', {}),
                'content_transformations': context.get('content_transformations', {}),
                'voice_audit_results': context.get('voice_audit_summary', {})
            }
            
            # Get prompt using wrapper system
            prompt, temperature = prompt_wrapper.get_guidelines_finalizer_prompt(
                comprehensive_insights=json.dumps(comprehensive_insights, indent=2),
                client_name=client_name,
                industry_context=context.get('industry', 'General'),
                workflow_summary="Complete 8-step Brand Builder workflow analysis"
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
                errors=[f"Guidelines finalization failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Finalize brand guidelines for Brand Builder')
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
    step = GuidelinesFinalizerTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Guidelines finalization successful!")
        print("🎉 Complete Brand Voice Guidelines generated!")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Final guidelines saved to {args.output}")
        else:
            print("📋 Guidelines Summary:")
            guidelines = result.data.get('brand_voice_guidelines', {})
            if isinstance(guidelines, dict):
                for key, value in list(guidelines.items())[:3]:  # Show first 3 sections
                    print(f"  {key}: {str(value)[:100]}...")
    else:
        print("❌ Guidelines finalization failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()