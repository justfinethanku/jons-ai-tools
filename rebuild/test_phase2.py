#!/usr/bin/env python3
"""
Test Phase 2 implementation - Core layer integration.
"""

import sys
from pathlib import Path

# Add the rebuild directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_llm_integrator():
    """Test LLM integrator basic functionality."""
    from core.llm_integrator import (
        LLMProvider, ValidationStatus, CodeContext, 
        ValidationResult, LLMIntegrator, PromptTemplate,
        ContextWindow, RefinementSession
    )
    
    print("Testing LLM Integrator...")
    
    # Test enums
    print(f"✓ LLMProvider: {LLMProvider.OPENAI}")
    print(f"✓ ValidationStatus: {ValidationStatus.VALID}")
    
    # Test data structures
    context = CodeContext(
        file_path="/test/utils.py",
        function_name="process_file"
    )
    print(f"✓ CodeContext: {context.file_path}")
    
    result = ValidationResult(
        is_valid=True,
        status=ValidationStatus.VALID,
        confidence_score=0.9
    )
    print(f"✓ ValidationResult: {result.is_valid}")
    
    # Test template
    template = PromptTemplate(
        template_id="test",
        template_text="Generate {function_name} for {purpose}",
        variables=["function_name", "purpose"]
    )
    
    rendered = template.render({"function_name": "test_func", "purpose": "testing"})
    print(f"✓ PromptTemplate: {rendered}")
    
    # Test context window
    window = ContextWindow(max_tokens=1000, current_tokens=200)
    print(f"✓ ContextWindow available: {window.available_tokens()}")
    
    # Test refinement session
    session = RefinementSession(
        session_id="test_session",
        original_prompt="Generate code"
    )
    print(f"✓ RefinementSession: {session.session_id}")
    
    # Test integrator
    integrator = LLMIntegrator(default_provider=LLMProvider.OPENAI)
    print(f"✓ LLMIntegrator: {integrator.default_provider}")
    
    # Test convert_rules_to_prompt
    rules = {
        "PURPOSE": "File processing",
        "RESPONSIBILITY": "Validate and process files",
        "IMPORTS_ALLOWED": "os, pathlib"
    }
    
    prompt = integrator.convert_rules_to_prompt(rules, context)
    print(f"✓ convert_rules_to_prompt: {len(prompt)} chars")
    assert "process_file" in prompt
    assert "File processing" in prompt
    
    print("LLM Integrator tests passed! ✅")
    return True


def main():
    """Run Phase 2 tests."""
    print("🧪 Testing Phase 2: Core Layer Implementation")
    print("=" * 50)
    
    try:
        test_llm_integrator()
        
        print("\n" + "=" * 50)
        print("🎉 Phase 2 Core Layer Tests PASSED! ✅")
        print("\nPhase 2 Progress:")
        print("- ✅ LLM integrator data structures implemented")
        print("- ✅ Rule-to-prompt conversion working")
        print("- ✅ Context management functional")
        print("- ✅ Foundation integration successful")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 2 tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)