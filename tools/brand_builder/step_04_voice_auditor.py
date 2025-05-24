"""
Step 4: Voice Auditor Tool

Audits voice consistency across content samples and brand guidelines.

Can be run independently for testing:
    python -m tools.brand_builder.step_04_voice_auditor --input step3_output.json --client "Test Client"
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.brand_builder import WorkflowStep, WorkflowContext, StepResult
from frameworks import universal_framework
from frameworks.prompt_wrappers import prompt_wrapper


class VoiceAuditorTool(WorkflowStep):
    """
    Step 4: Voice Auditor - Audits voice consistency across content samples
    """
    
    def get_required_inputs(self):
        return ['client_name', 'content_samples']
    
    def get_dependencies(self):
        return ['step_03_content_collector']
    
    def get_output_fields(self):
        return ['voice_audit_summary', 'content_analysis', 'voice_patterns']
    
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute voice audit"""
        client_name = context.get('client_name')
        
        try:
            # Build brand profile for analysis
            brand_profile = f"""
**BRAND PROFILE:**
- Company: {client_name}
- Mission: {context.get('brand_mission', 'Not specified')}
- Values: {context.get('brand_values', 'Not specified')}
- Personality: {context.get('brand_personality_traits', 'Not specified')}
- Target Audience: {context.get('ideal_target_audience', 'Not specified')}
- Communication Tone: {context.get('communication_tone', 'Not specified')}"""
            
            content_samples = json.dumps(context.get('content_samples', []), indent=2)
            industry_context = f"Industry: {context.get('industry', 'General')}"
            
            # Get prompt using wrapper system
            prompt, temperature = prompt_wrapper.get_voice_audit_prompt(
                brand_profile=brand_profile,
                content_samples=content_samples,
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
            
            # Parse response (implement robust parsing if needed)
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
                errors=[f"Voice audit failed: {str(e)}"],
                warnings=[],
                step_name=self.name
            )


def main():
    """CLI interface for testing step independently"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit voice consistency for Brand Builder')
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
    step = VoiceAuditorTool()
    result = step.execute(context)
    
    # Output results
    if result.success:
        print("✅ Voice audit successful!")
        print(f"📊 Analysis complete")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.data, f, indent=2)
            print(f"💾 Results saved to {args.output}")
    else:
        print("❌ Voice audit failed!")
        for error in result.errors:
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()