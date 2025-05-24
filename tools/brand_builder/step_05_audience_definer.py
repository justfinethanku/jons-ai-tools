"""
Step 5: Audience Definer Tool

Develops detailed audience personas based on brand insights and content analysis.

Can be run independently for testing:
    python -m tools.brand_builder.step_05_audience_definer --input step4_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class AudienceDefinerTool(WorkflowStep):
    """
    Step 5: Audience Definer - Develops detailed audience personas
    """
    
    def get_required_inputs(self):
        return ['client_name']
    
    def get_dependencies(self):
        return ['step_04_voice_auditor']
    
    def get_output_fields(self):
        return ['detailed_personas', 'audience_segments', 'persona_insights']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute audience definition"""
        client_name = context.get('client_name')
        
        try:
            # Build context from previous steps
            brand_context = f"""
**BRAND CONTEXT:**
- Company: {client_name}
- Industry: {context.get('industry', 'Unknown')}
- Target Audience: {context.get('ideal_target_audience', 'Not specified')}
- Brand Values: {context.get('brand_values', 'Not specified')}"""
            
            content_insights = json.dumps(context.get('content_samples', []), indent=2)
            voice_insights = json.dumps(context.get('voice_audit_summary', {}), indent=2)
            industry_context = f"Industry: {context.get('industry', 'General')}"
            
            # Get prompt using wrapper system
            prompt, temperature = prompt_wrapper.get_audience_definer_prompt(
                brand_context=brand_context,
                content_insights=content_insights,
                voice_insights=voice_insights,
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
                errors=[f"Audience definition failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Define audience personas for Brand Builder')
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
    step = AudienceDefinerTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Audience definition successful!")
        print(f"📊 Analysis complete")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
    else:
        print("❌ Audience definition failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()