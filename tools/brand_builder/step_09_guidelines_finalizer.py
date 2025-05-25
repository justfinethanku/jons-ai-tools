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
    
    def validate_context(self, context: WorkflowContext):
        """Validate context data and return (is_valid, errors, warnings)"""
        errors = []
        warnings = []
        
        # Check required fields
        if not context.get('client_name'):
            errors.append("Missing required field: client_name")
        
        # Check recommended fields for quality
        recommended_fields = {
            'brand_mission': 'Brand mission is core to final guidelines',
            'brand_values': 'Brand values shape guideline principles',
            'brand_personality_traits': 'Personality traits define voice characteristics',
            'detailed_personas': 'Audience personas inform guideline targeting',
            'voice_traits': 'Voice traits form the framework foundation',
            'content_samples': 'Content samples provide implementation examples',
            'strategic_gaps': 'Gap analysis informs improvement recommendations',
            'content_transformations': 'Content transformations demonstrate application',
            'voice_audit_summary': 'Voice audit provides baseline and progress'
        }
        
        for field, reason in recommended_fields.items():
            if not context.get(field):
                warnings.append(f"Missing recommended field '{field}': {reason}")
        
        return len(errors) == 0, errors, warnings
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute guidelines finalization"""
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
            
            # Define API schema for validation
            api_schema = {
                "type": "object",
                "properties": {
                    "brand_voice_guidelines": {"type": "object"},
                    "implementation_roadmap": {"type": "array", "items": {"type": "object"}},
                    "final_document": {"type": "string"}
                },
                "required": ["brand_voice_guidelines", "implementation_roadmap", "final_document"]
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
                errors=[f"Guidelines finalization failed: {str(e)}"],
                warnings=warnings,
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