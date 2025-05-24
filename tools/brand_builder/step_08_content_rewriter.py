"""
Step 8: Content Rewriter Tool

Transforms content samples based on brand insights and voice guidelines.

Can be run independently for testing:
    python -m tools.brand_builder.step_08_content_rewriter --input step7_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class ContentRewriterTool(WorkflowStep):
    """
    Step 8: Content Rewriter - Transforms content samples based on brand insights
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_07_gap_analyzer']
    
    def get_output_fields(self):
        return ['content_transformations', 'rewrite_examples', 'implementation_guide']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute content rewriting"""
        client_name = context.get('client_name')
        
        try:
            # Build comprehensive insights for content transformation
            transformation_context = {
                'brand_voice': context.get('voice_traits', {}),
                'audience_insights': context.get('detailed_personas', {}),
                'competitive_gaps': context.get('strategic_gaps', {}),
                'content_samples': context.get('content_samples', [])
            }
            
            brand_guidelines = json.dumps({
                'mission': context.get('brand_mission'),
                'values': context.get('brand_values'),
                'personality': context.get('brand_personality_traits'),
                'voice_traits': context.get('voice_traits', {})
            }, indent=2)
            
            # Get prompt using wrapper system
            prompt, temperature = prompt_wrapper.get_content_rewriter_prompt(
                transformation_context=json.dumps(transformation_context, indent=2),
                brand_guidelines=brand_guidelines,
                gap_insights=json.dumps(context.get('strategic_gaps', {})),
                content_samples=json.dumps(context.get('content_samples', []))
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
                errors=[f"Content rewriting failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rewrite content for Brand Builder')
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
    step = ContentRewriterTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Content rewriting successful!")
        print(f"📊 Analysis complete")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
    else:
        print("❌ Content rewriting failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()