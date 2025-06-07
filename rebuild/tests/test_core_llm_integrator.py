"""
Test suite for core/llm_integrator.py module.

Tests LLM integration functionality including rule-to-prompt conversion,
context management, response validation, and iterative refinement.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from enum import Enum
import json

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.llm_integrator import (
    LLMProvider,
    ValidationStatus,
    CodeContext,
    ValidationResult,
    LLMIntegrator,
    PromptTemplate,
    ContextWindow,
    RefinementSession
)


class TestLLMProvider:
    """Test LLMProvider enumeration."""
    
    def test_provider_values(self):
        """Test that all expected providers are available."""
        expected_providers = ['OPENAI', 'ANTHROPIC', 'GEMINI', 'LOCAL']
        actual_providers = [provider.name for provider in LLMProvider]
        
        for provider in expected_providers:
            assert provider in actual_providers


class TestValidationStatus:
    """Test ValidationStatus enumeration."""
    
    def test_validation_statuses(self):
        """Test that all expected validation statuses are available."""
        expected_statuses = ['VALID', 'SYNTAX_ERROR', 'RULE_VIOLATION', 'INCOMPLETE', 'INVALID']
        actual_statuses = [status.name for status in ValidationStatus]
        
        for status in expected_statuses:
            assert status in actual_statuses


class TestCodeContext:
    """Test CodeContext data structure."""
    
    def test_code_context_creation(self):
        """Test creation of code context."""
        context = CodeContext(
            file_path="/test/file.py",
            function_name="test_function",
            class_name="TestClass",
            imports=["import os", "import sys"],
            dependencies=["dependency1", "dependency2"],
            rules={"rule1": "value1", "rule2": "value2"}
        )
        
        assert context.file_path == "/test/file.py"
        assert context.function_name == "test_function"
        assert context.class_name == "TestClass"
        assert len(context.imports) == 2
        assert len(context.dependencies) == 2
        assert len(context.rules) == 2
    
    def test_code_context_defaults(self):
        """Test default values in code context."""
        context = CodeContext(
            file_path="/test/file.py"
        )
        
        assert context.file_path == "/test/file.py"
        assert context.function_name is None
        assert context.class_name is None
        assert context.imports == []
        assert context.dependencies == []
        assert context.rules == {}


class TestValidationResult:
    """Test ValidationResult data structure."""
    
    def test_validation_result_valid(self):
        """Test creation of valid validation result."""
        result = ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=["Consider adding type hints"],
            confidence_score=0.95
        )
        
        assert result.status == ValidationStatus.VALID
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.suggestions) == 1
        assert result.confidence_score == 0.95
    
    def test_validation_result_invalid(self):
        """Test creation of invalid validation result."""
        result = ValidationResult(
            status=ValidationStatus.SYNTAX_ERROR,
            is_valid=False,
            errors=["Syntax error on line 5"],
            warnings=["Unused import"],
            suggestions=["Fix syntax error"],
            confidence_score=0.1
        )
        
        assert result.status == ValidationStatus.SYNTAX_ERROR
        assert result.is_valid == False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.confidence_score == 0.1


class TestPromptTemplate:
    """Test PromptTemplate functionality."""
    
    def test_prompt_template_creation(self):
        """Test creation of prompt template."""
        template = PromptTemplate(
            template_id="test_template",
            template_text="Generate code for {function_name} with rules: {rules}",
            variables=["function_name", "rules"],
            context_requirements=["function_name", "rules"],
            provider_specific={"openai": {"temperature": 0.7}, "anthropic": {"temperature": 0.5}}
        )
        
        assert template.template_id == "test_template"
        assert "{function_name}" in template.template_text
        assert "function_name" in template.variables
        assert "rules" in template.context_requirements
        assert "openai" in template.provider_specific
    
    def test_prompt_template_rendering(self):
        """Test rendering of prompt template."""
        template = PromptTemplate(
            template_id="test_template",
            template_text="Generate code for {function_name} with rules: {rules}",
            variables=["function_name", "rules"]
        )
        
        rendered = template.render({
            "function_name": "test_func",
            "rules": ["rule1", "rule2"]
        })
        
        assert "test_func" in rendered
        assert "rule1" in rendered or "rule2" in rendered


class TestContextWindow:
    """Test ContextWindow management."""
    
    def test_context_window_creation(self):
        """Test creation of context window."""
        window = ContextWindow(
            max_tokens=4000,
            current_tokens=1000,
            context_data={"key": "value"},
            priority_items=["item1", "item2"],
            overflow_strategy="truncate"
        )
        
        assert window.max_tokens == 4000
        assert window.current_tokens == 1000
        assert window.context_data["key"] == "value"
        assert len(window.priority_items) == 2
        assert window.overflow_strategy == "truncate"
    
    def test_context_window_capacity(self):
        """Test context window capacity management."""
        window = ContextWindow(
            max_tokens=4000,
            current_tokens=3800
        )
        
        available = window.available_tokens()
        assert available == 200
        
        is_full = window.is_near_capacity(threshold=0.9)
        assert is_full == True


class TestRefinementSession:
    """Test RefinementSession functionality."""
    
    def test_refinement_session_creation(self):
        """Test creation of refinement session."""
        session = RefinementSession(
            session_id="test_session",
            original_prompt="Generate a function",
            iterations=[],
            current_iteration=0,
            max_iterations=5,
            convergence_criteria={"min_confidence": 0.9}
        )
        
        assert session.session_id == "test_session"
        assert session.original_prompt == "Generate a function"
        assert session.current_iteration == 0
        assert session.max_iterations == 5
        assert session.convergence_criteria["min_confidence"] == 0.9
    
    def test_refinement_session_iteration(self):
        """Test adding iterations to refinement session."""
        session = RefinementSession(
            session_id="test_session",
            original_prompt="Generate a function",
            iterations=[],
            current_iteration=0,
            max_iterations=5
        )
        
        iteration_data = {
            "prompt": "Refined prompt",
            "response": "Generated code",
            "validation": ValidationResult(
                status=ValidationStatus.VALID,
                is_valid=True,
                confidence_score=0.8
            )
        }
        
        session.add_iteration(iteration_data)
        
        assert session.current_iteration == 1
        assert len(session.iterations) == 1
        assert session.iterations[0]["prompt"] == "Refined prompt"


class TestLLMIntegrator:
    """Test LLMIntegrator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_client = Mock()
        self.mock_rule_engine = Mock()
        
        self.integrator = LLMIntegrator(
            ai_client=self.mock_ai_client,
            rule_engine=self.mock_rule_engine,
            default_provider=LLMProvider.OPENAI
        )
    
    def test_llm_integrator_creation(self):
        """Test creation of LLM integrator."""
        assert self.integrator is not None
        assert self.integrator.default_provider == LLMProvider.OPENAI
    
    def test_convert_rules_to_prompt(self):
        """Test conversion of rules to prompts."""
        rules = {
            "PURPOSE": "Generate a utility function",
            "RESPONSIBILITY": "File processing",
            "IMPORTS_ALLOWED": "os, sys, pathlib",
            "IMPORTS_FORBIDDEN": "requests, urllib"
        }
        
        context = CodeContext(
            file_path="/test/utils.py",
            function_name="process_file"
        )
        
        prompt = self.integrator.convert_rules_to_prompt(rules, context)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "PURPOSE" in prompt or "utility function" in prompt
        assert "process_file" in prompt
    
    def test_validate_code_response(self):
        """Test validation of code responses."""
        code_response = '''
def test_function():
    """Test function implementation."""
    return "Hello, World!"
        '''
        
        rules = {
            "SYNTAX_CHECK": "true",
            "RULE_COMPLIANCE": "true"
        }
        
        result = self.integrator.validate_code_response(code_response, rules)
        
        assert isinstance(result, ValidationResult)
        assert result.status in ValidationStatus
        assert isinstance(result.is_valid, bool)
    
    def test_generate_code_with_rules(self):
        """Test code generation with rules."""
        # Mock the AI client response
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = '''
def test_function():
    """Generated test function."""
    return "test"
        '''
        self.mock_ai_client.make_request.return_value = mock_response
        
        rules = {
            "PURPOSE": "Generate a test function",
            "RESPONSIBILITY": "Return test string"
        }
        
        context = CodeContext(
            file_path="/test/test.py",
            function_name="test_function"
        )
        
        result = self.integrator.generate_code_with_rules(rules, context)
        
        assert result is not None
        assert "def test_function" in result
        self.mock_ai_client.make_request.assert_called_once()
    
    def test_iterative_refinement(self):
        """Test iterative refinement process."""
        # Mock AI client responses for refinement
        responses = [
            Mock(success=True, content="def func(): pass"),  # First attempt
            Mock(success=True, content="def func():\n    return 'refined'")  # Refined attempt
        ]
        self.mock_ai_client.make_request.side_effect = responses
        
        rules = {"PURPOSE": "Generate a function"}
        context = CodeContext(file_path="/test/test.py")
        convergence_criteria = {"min_confidence": 0.9, "max_iterations": 3}
        
        session = self.integrator.iterative_refinement(rules, context, convergence_criteria)
        
        assert isinstance(session, RefinementSession)
        assert len(session.iterations) > 0
        assert session.current_iteration > 0
    
    def test_manage_context_window(self):
        """Test context window management."""
        large_context = {
            "rules": {"rule_" + str(i): "value_" + str(i) for i in range(100)},
            "code": "def function(): pass" * 100,
            "imports": ["import module_" + str(i) for i in range(50)]
        }
        
        max_tokens = 1000
        managed_context = self.integrator.manage_context_window(large_context, max_tokens)
        
        assert isinstance(managed_context, dict)
        # Context should be reduced to fit within token limit
        estimated_tokens = self.integrator.estimate_context_tokens(managed_context)
        assert estimated_tokens <= max_tokens
    
    def test_extract_code_from_response(self):
        """Test extraction of code from LLM responses."""
        response_with_code = '''
Here's the implementation:

```python
def test_function():
    """Test function."""
    return "Hello, World!"
```

This function does what you requested.
        '''
        
        extracted_code = self.integrator.extract_code_from_response(response_with_code)
        
        assert "def test_function" in extracted_code
        assert "Hello, World!" in extracted_code
        assert "Here's the implementation" not in extracted_code
    
    def test_apply_rule_constraints(self):
        """Test application of rule constraints to prompts."""
        base_prompt = "Generate a utility function"
        
        rules = {
            "IMPORTS_ALLOWED": "os, sys",
            "IMPORTS_FORBIDDEN": "requests",
            "STYLE": "functional",
            "MAX_LINES": "20"
        }
        
        constrained_prompt = self.integrator.apply_rule_constraints(base_prompt, rules)
        
        assert isinstance(constrained_prompt, str)
        assert len(constrained_prompt) > len(base_prompt)
        assert "os, sys" in constrained_prompt
        assert "requests" in constrained_prompt
        assert "20" in constrained_prompt
    
    def test_provider_specific_formatting(self):
        """Test provider-specific prompt formatting."""
        base_prompt = "Generate code"
        
        openai_prompt = self.integrator.format_for_provider(base_prompt, LLMProvider.OPENAI)
        anthropic_prompt = self.integrator.format_for_provider(base_prompt, LLMProvider.ANTHROPIC)
        
        assert isinstance(openai_prompt, str)
        assert isinstance(anthropic_prompt, str)
        # Different providers might have different formatting
        assert len(openai_prompt) > 0
        assert len(anthropic_prompt) > 0
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        # Mock AI client failure
        self.mock_ai_client.make_request.side_effect = Exception("API Error")
        
        rules = {"PURPOSE": "Generate code"}
        context = CodeContext(file_path="/test/test.py")
        
        # Should handle error gracefully
        result = self.integrator.generate_code_with_rules(rules, context)
        
        # Should return error indication or fallback
        assert result is not None
    
    def test_confidence_scoring(self):
        """Test confidence scoring for generated code."""
        code = '''
def well_documented_function(param: str) -> str:
    """
    Well-documented function with type hints.
    
    Args:
        param: Input parameter
        
    Returns:
        Processed string
    """
    return param.upper()
        '''
        
        rules = {
            "DOCUMENTATION": "required",
            "TYPE_HINTS": "required"
        }
        
        confidence = self.integrator.calculate_confidence_score(code, rules)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        # Well-documented code with type hints should have high confidence
        assert confidence > 0.7
    
    def test_rule_compliance_checking(self):
        """Test checking rule compliance in generated code."""
        code_with_forbidden_import = '''
import requests  # This should be forbidden
import os       # This should be allowed

def function():
    return "test"
        '''
        
        rules = {
            "IMPORTS_ALLOWED": "os, sys",
            "IMPORTS_FORBIDDEN": "requests, urllib"
        }
        
        violations = self.integrator.check_rule_compliance(code_with_forbidden_import, rules)
        
        assert isinstance(violations, list)
        assert len(violations) > 0
        # Should detect the forbidden import
        assert any("requests" in violation for violation in violations)


class TestIntegrationScenarios:
    """Test integration scenarios with multiple components."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_ai_client = Mock()
        self.mock_rule_engine = Mock()
        
        self.integrator = LLMIntegrator(
            ai_client=self.mock_ai_client,
            rule_engine=self.mock_rule_engine,
            default_provider=LLMProvider.OPENAI
        )
    
    def test_end_to_end_code_generation(self):
        """Test end-to-end code generation workflow."""
        # Mock rule engine response
        self.mock_rule_engine.get_rules_for_context.return_value = {
            "PURPOSE": "Generate file utility",
            "IMPORTS_ALLOWED": "pathlib, os",
            "STYLE": "functional"
        }
        
        # Mock AI client response
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = '''
```python
from pathlib import Path
import os

def process_file(file_path: str) -> bool:
    """Process a file according to rules."""
    path = Path(file_path)
    return path.exists()
```
        '''
        self.mock_ai_client.make_request.return_value = mock_response
        
        # Execute end-to-end workflow
        context = CodeContext(
            file_path="/utils/file_utils.py",
            function_name="process_file"
        )
        
        result = self.integrator.generate_with_full_pipeline(context)
        
        assert result is not None
        assert "def process_file" in result
        assert "pathlib" in result or "Path" in result
        
        # Verify calls were made
        self.mock_rule_engine.get_rules_for_context.assert_called_once()
        self.mock_ai_client.make_request.assert_called_once()
    
    def test_refinement_with_feedback_loop(self):
        """Test refinement process with feedback loop."""
        # Mock initial poor response
        initial_response = Mock()
        initial_response.success = True
        initial_response.content = "def func(): pass"  # Too simple
        
        # Mock refined response
        refined_response = Mock()
        refined_response.success = True
        refined_response.content = '''
def process_data(data: list) -> dict:
    """Process data according to specifications."""
    result = {}
    for item in data:
        result[item] = len(item)
    return result
        '''
        
        self.mock_ai_client.make_request.side_effect = [initial_response, refined_response]
        
        context = CodeContext(
            file_path="/utils/data_utils.py",
            function_name="process_data"
        )
        
        rules = {
            "PURPOSE": "Process data into dictionary",
            "TYPE_HINTS": "required",
            "DOCUMENTATION": "required"
        }
        
        session = self.integrator.iterative_refinement(
            rules, 
            context, 
            {"min_confidence": 0.8, "max_iterations": 3}
        )
        
        assert session.current_iteration >= 1
        assert len(session.iterations) >= 1
        # Should have improved through refinement
        final_code = session.iterations[-1]["response"]
        assert "def process_data" in final_code
        assert ":" in final_code  # Should have type hints


if __name__ == "__main__":
    pytest.main([__file__])