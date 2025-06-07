"""
@RULE:LAYER: core/__init__
@RULE:FORBIDDEN: tools.*, shared.*, tests.*, main
@SEE: core/CLAUDE.md#common-interfaces
Core module package initialization and public API definition
"""

# Core module version for API compatibility tracking
__version__ = "1.0.0"

# Allowed imports - core modules only
# from .rule_parser import RuleParser
# from .rule_engine import RuleEngine, ArchitecturalRule, ComplianceResult
# from .llm_integrator import LLMIntegrator, ValidationResult
# from .code_analyzer import CodeAnalyzer, DependencyGraph, InterfaceReport
# from .execution_environment import ExecutionEnvironment, CodeContext

# Public API definition - what external modules can import
__all__ = [
    # Core classes that external modules can use
    "RuleParser",
    "RuleEngine", 
    "LLMIntegrator",
    "CodeAnalyzer",
    "ExecutionEnvironment",
    
    # Data structures for inter-module communication
    "ArchitecturalRule",
    "ComplianceResult", 
    "ValidationResult",
    "DependencyGraph",
    "InterfaceReport",
    "CodeContext",
    
    # Version information
    "__version__"
]

# Architectural validation at module level
def _validate_core_integrity():
    """
    Private function to validate core module architectural integrity.
    
    This ensures all core modules follow the established rules and
    maintain proper dependency direction.
    """
    # Implementation would validate:
    # - No circular dependencies between core modules
    # - All modules follow naming conventions
    # - Public APIs are properly defined
    # - Rule comments are present and valid
    pass

# Initialize core module integrity validation
# _validate_core_integrity()