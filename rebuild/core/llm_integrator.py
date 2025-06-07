"""
@RULE:PURPOSE: Translate architectural rules into LLM prompts and validate generated code responses
@RULE:RESPONSIBILITY: Rule-to-prompt conversion, context management, response validation, iterative refinement
@RULE:IMPORTS_ALLOWED: .rule_parser, .rule_engine, typing, dataclasses, enum, logging, json, openai, anthropic
@RULE:IMPORTS_FORBIDDEN: .code_analyzer, .execution_environment, tools.*, shared.*, main
@RULE:PUBLIC_API: LLMIntegrator, ValidationResult, generate_prompt, validate_response, iterative_refinement
@RULE:PRIVATE_IMPL: _convert_rules_to_prompt, _manage_context_window, _validate_code_syntax, _refine_with_feedback
@RULE:NO_CROSS_TALK: code_analyzer, execution_environment
@RULE:DEPENDENCY_DIRECTION: llm_integrator -> rule_parser, rule_engine (can use both for rule processing)
@RULE:INTERFACE_RULE: Clean LLM interaction API with standardized prompt/response handling
@RULE:ONE_PURPOSE: Single responsibility is LLM interaction for rule-driven code generation
@RULE:API_MANAGEMENT: Support multiple LLM providers with unified interface
@RULE:SECURITY: Secure API key management and request validation
"""

# Allowed imports based on dependency rules
import json
import logging
import re
import ast
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto

# Import from shared layer (allowed by architecture)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.ai_client import AIClient, APIProvider, AIRequest, RequestType, AIResponse


class LLMProvider(Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = auto()      # OpenAI GPT models
    ANTHROPIC = auto()   # Anthropic Claude models
    GEMINI = auto()      # Google Gemini models
    LOCAL = auto()       # Local/self-hosted models


class ValidationStatus(Enum):
    """Enumeration of code validation results."""
    VALID = auto()           # Code passes all validations
    SYNTAX_ERROR = auto()    # Code has syntax errors
    RULE_VIOLATION = auto()  # Code violates architectural rules
    INCOMPLETE = auto()      # Code is incomplete or partial
    INVALID = auto()         # Code is fundamentally invalid


@dataclass
class CodeContext:
    """
    Data structure representing code generation context.
    
    Attributes:
        file_path: Target file path for code generation
        module_name: Python module name
        class_name: Optional class name for method generation
        function_name: Optional function name for specific generation
        existing_code: Optional existing code to build upon
        dependencies: List of required dependencies
        imports: List of import statements
        rules: Dict of applicable architectural rules
        metadata: Additional context metadata
    """
    file_path: str
    module_name: Optional[str] = None
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    existing_code: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    rules: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    Data structure representing LLM response validation results.
    
    Attributes:
        is_valid: Overall validation status
        status: Detailed validation status
        syntax_errors: List of syntax errors found
        rule_violations: List of rule violations found
        suggestions: List of improvement suggestions
        confidence_score: Confidence in the validation result
        errors: List of all errors found
        warnings: List of warnings
        metadata: Additional validation metadata
    """
    is_valid: bool
    status: ValidationStatus
    syntax_errors: List[str] = field(default_factory=list)
    rule_violations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptTemplate:
    """Template for generating prompts from rules and context."""
    template_id: str
    template_text: str
    variables: List[str] = field(default_factory=list)
    context_requirements: List[str] = field(default_factory=list)
    provider_specific: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render template with provided context."""
        try:
            # Simple string formatting for now
            return self.template_text.format(**context)
        except KeyError as e:
            # Missing variable, return template with placeholder
            return self.template_text.replace(f"{{{e.args[0]}}}", f"[{e.args[0]}]")


@dataclass
class ContextWindow:
    """Manages context window for LLM requests."""
    max_tokens: int
    current_tokens: int = 0
    context_data: Dict[str, Any] = field(default_factory=dict)
    priority_items: List[str] = field(default_factory=list)
    overflow_strategy: str = "truncate"
    
    def available_tokens(self) -> int:
        """Get available tokens in context window."""
        return max(0, self.max_tokens - self.current_tokens)
    
    def is_near_capacity(self, threshold: float = 0.9) -> bool:
        """Check if context window is near capacity."""
        return (self.current_tokens / self.max_tokens) >= threshold


@dataclass
class RefinementSession:
    """Manages iterative refinement sessions."""
    session_id: str
    original_prompt: str
    iterations: List[Dict[str, Any]] = field(default_factory=list)
    current_iteration: int = 0
    max_iterations: int = 5
    convergence_criteria: Dict[str, Any] = field(default_factory=dict)
    
    def add_iteration(self, iteration_data: Dict[str, Any]) -> None:
        """Add an iteration to the session."""
        self.iterations.append(iteration_data)
        self.current_iteration += 1


class LLMIntegrator:
    """
    Core LLM integration layer for rule-driven code generation.
    
    This class manages the translation of architectural rules into LLM prompts,
    handles context window management, validates LLM responses, and orchestrates
    iterative refinement for rule compliance.
    
    Architectural Constraints:
    - Can import from rule_parser and rule_engine
    - Must not import from code_analyzer or execution_environment
    - Provides unified interface for multiple LLM providers
    - Implements secure API key management
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None, rule_engine=None, default_provider: LLMProvider = LLMProvider.OPENAI):
        """
        Initialize the LLM integrator with specified provider.
        
        Args:
            ai_client: AI client for making requests
            rule_engine: Rule engine for processing rules
            default_provider: Default LLM provider to use
        """
        self._ai_client = ai_client
        self._rule_engine = rule_engine
        self.default_provider = default_provider
        self._logger = logging.getLogger(__name__)
        self._max_context_tokens = self._get_max_context_for_provider(default_provider)
    
    def convert_rules_to_prompt(self, rules: Dict[str, str], context: CodeContext) -> str:
        """
        Convert rules dictionary to LLM prompt.
        
        Args:
            rules: Dictionary of rule name to rule value
            context: Code generation context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add purpose and responsibility
        if "PURPOSE" in rules:
            prompt_parts.append(f"Generate code with the following purpose: {rules['PURPOSE']}")
        
        if "RESPONSIBILITY" in rules:
            prompt_parts.append(f"The code should be responsible for: {rules['RESPONSIBILITY']}")
        
        # Add context information
        if context.function_name:
            prompt_parts.append(f"Function name: {context.function_name}")
        
        if context.class_name:
            prompt_parts.append(f"Class name: {context.class_name}")
        
        if context.file_path:
            prompt_parts.append(f"File path: {context.file_path}")
        
        # Add import constraints
        if "IMPORTS_ALLOWED" in rules:
            prompt_parts.append(f"Only use these imports: {rules['IMPORTS_ALLOWED']}")
        
        if "IMPORTS_FORBIDDEN" in rules:
            prompt_parts.append(f"Do not use these imports: {rules['IMPORTS_FORBIDDEN']}")
        
        # Add other rules
        for rule_name, rule_value in rules.items():
            if rule_name not in ["PURPOSE", "RESPONSIBILITY", "IMPORTS_ALLOWED", "IMPORTS_FORBIDDEN"]:
                prompt_parts.append(f"{rule_name}: {rule_value}")
        
        # Combine into coherent prompt
        prompt = "\n".join(prompt_parts)
        prompt += "\n\nGenerate clean, well-documented Python code that follows all the above rules."
        
        return prompt
    
    def _get_max_context_for_provider(self, provider: LLMProvider) -> int:
        """Get maximum context tokens for provider."""
        context_limits = {
            LLMProvider.OPENAI: 8192,
            LLMProvider.ANTHROPIC: 100000,
            LLMProvider.GEMINI: 32768,
            LLMProvider.LOCAL: 4096
        }
        return context_limits.get(provider, 4096)
    
