"""
Step 7: Gap Analyzer Tool

Identifies competitive intelligence and strategic gaps in brand positioning.

Can be run independently for testing:
    python -m tools.brand_builder.step_07_gap_analyzer --input step6_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class GapAnalyzerTool(WorkflowStep):
    """
    Step 7: Gap Analyzer - Identifies competitive intelligence and strategic gaps
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_06_voice_traits_builder']
    
    def get_output_fields(self):
        return ['competitive_analysis', 'strategic_gaps', 'opportunities']
    
    def validate_context(self, context: WorkflowContext):
        """Validate context data and return (is_valid, errors, warnings)"""
        errors = []
        warnings = []
        
        # Check required fields
        if not context.get('client_name'):
            errors.append("Missing required field: client_name")
        
        # Check recommended fields for quality
        recommended_fields = {
            'industry': 'Industry context is essential for competitive analysis',
            'voice_traits': 'Voice traits help identify positioning gaps',
            'detailed_personas': 'Audience personas guide gap identification',
            'brand_values': 'Brand values inform competitive differentiation',
            'competitive_differentiation': 'Existing differentiation data improves analysis'
        }
        
        for field, reason in recommended_fields.items():
            if not context.get(field):
                warnings.append(f"Missing recommended field '{field}': {reason}")
        
        return len(errors) == 0, errors, warnings
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute gap analysis"""
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
            # Build comprehensive context for competitive analysis
            brand_positioning = {
                'company': client_name,
                'industry': context.get('industry'),
                'voice_traits': context.get('voice_traits', {}),
                'audience_personas': context.get('detailed_personas', {}),
                'brand_values': context.get('brand_values'),
                'differentiation': context.get('competitive_differentiation')
            }
            
            market_context = f"Industry: {context.get('industry', 'General')} market analysis"
            voice_strategy = json.dumps(context.get('voice_traits', {}), indent=2)
            
            # Get prompt using wrapper system
            prompt, temperature = prompt_wrapper.get_gap_analyzer_prompt(
                brand_positioning=json.dumps(brand_positioning, indent=2),
                market_context=market_context,
                voice_strategy=voice_strategy,
                competitive_context=context.get('competitive_differentiation', 'Not specified')
            )
            
            # Define API schema for validation
            api_schema = {
                "type": "object",
                "properties": {
                    "competitive_analysis": {"type": "object"},
                    "strategic_gaps": {"type": "array", "items": {"type": "object"}},
                    "opportunities": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["competitive_analysis", "strategic_gaps", "opportunities"]
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
                errors=[f"Gap analysis failed: {str(e)}"],
                warnings=warnings,
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze competitive gaps for Brand Builder')
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
    step = GapAnalyzerTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Gap analysis successful!")
        print(f"📊 Analysis complete")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
    else:
        print("❌ Gap analysis failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()