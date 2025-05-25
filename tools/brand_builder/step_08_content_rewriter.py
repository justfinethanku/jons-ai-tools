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
    
    def validate_context(self, context: WorkflowContext):
        """Validate context data and return (is_valid, errors, warnings)"""
        errors = []
        warnings = []
        
        # Check required fields
        if not context.get('client_name'):
            errors.append("Missing required field: client_name")
        
        # Check recommended fields for quality
        recommended_fields = {
            'voice_traits': 'Voice traits guide content transformation',
            'detailed_personas': 'Audience personas inform content targeting',
            'strategic_gaps': 'Gap analysis provides improvement direction',
            'content_samples': 'Content samples are needed for rewriting examples',
            'brand_mission': 'Brand mission aligns content purpose',
            'brand_values': 'Brand values ensure content consistency'
        }
        
        for field, reason in recommended_fields.items():
            if not context.get(field):
                warnings.append(f"Missing recommended field '{field}': {reason}")
        
        return len(errors) == 0, errors, warnings
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute content rewriting"""
        # Validate context first
        is_valid, errors, warnings = self.validate_context(context)
        if not is_valid:
            return StepResult(
                success=False,
                data={},
                errors=errors,
                warnings=warnings,
                step_name=self.name
            )
        
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
            
            # Define API schema for validation
            api_schema = {
                "type": "object",
                "properties": {
                    "content_transformations": {"type": "array", "items": {"type": "object"}},
                    "rewrite_examples": {"type": "array", "items": {"type": "object"}},
                    "implementation_guide": {"type": "object"}
                },
                "required": ["content_transformations", "rewrite_examples", "implementation_guide"]
            }
            
            # Call API with schema validation
            response = universal_framework.call_gemini_api(prompt, response_schema=api_schema, temperature=temperature)
            
            # Check for API error responses
            if response.startswith("Error:"):
                return StepResult(
                    success=False,
                    data={},
                    errors=[f"API call failed: {response}"],
                    warnings=warnings,
                    step_name=self.name
                )
            
            # Parse response with error handling
            try:
                result_data = json.loads(response)
            except json.JSONDecodeError as e:
                return StepResult(
                    success=False,
                    data={},
                    errors=[f"Failed to parse API response: {str(e)}"],
                    warnings=warnings,
                    step_name=self.name
                )
            
            return StepResult(
                success=True,
                data=result_data,
                errors=[],
                warnings=warnings,
                step_name=self.name
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                data={},
                errors=[f"Content rewriting failed: {str(e)}"],
                warnings=warnings,
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