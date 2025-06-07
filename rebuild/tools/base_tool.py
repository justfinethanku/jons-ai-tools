"""
@RULE:PURPOSE: Define base tool interface and common tool functionality for rule-driven development tools
@RULE:RESPONSIBILITY: Tool interface definition, metadata management, result standardization, lifecycle management
@RULE:IMPORTS_ALLOWED: typing, abc, dataclasses, enum, logging, pathlib
@RULE:IMPORTS_FORBIDDEN: core.*, shared.*, main, other tools
@RULE:PUBLIC_API: BaseTool, ToolMetadata, ToolResult, ToolStatus, execute, validate, configure
@RULE:PRIVATE_IMPL: _validate_input, _process_result, _handle_error, _log_execution
@RULE:NO_CROSS_TALK: core modules, shared utilities, main application, other tools
@RULE:DEPENDENCY_DIRECTION: base_tool -> standard library only (no external dependencies)
@RULE:INTERFACE_RULE: Abstract base class defining standardized tool interface
@RULE:ONE_PURPOSE: Single responsibility is tool interface definition and common functionality
@RULE:EXTENSIBILITY: Designed for inheritance by concrete tool implementations
@RULE:THREAD_SAFETY: Thread-safe base implementation for concurrent tool execution
"""

# Allowed imports - standard library only
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class ToolStatus(Enum):
    """Enumeration of tool execution status."""
    SUCCESS = auto()         # Tool execution completed successfully
    ERROR = auto()           # Tool execution failed
    PENDING = auto()         # Tool execution pending
    RUNNING = auto()         # Tool currently executing
    CANCELLED = auto()       # Tool execution cancelled
    TIMEOUT = auto()         # Tool execution timed out


class ToolCapability(Enum):
    """Enumeration of tool capabilities."""
    TEXT_PROCESSING = auto()     # Process and transform text
    AI_INTEGRATION = auto()      # Integrate with AI services
    RULE_PROCESSING = auto()     # Process architectural rules
    TEMPLATE_PROCESSING = auto() # Process templates
    CONTEXT_AWARE = auto()       # Context-aware processing
    PROMPT_REFINEMENT = auto()   # Refine and improve prompts
    CONTENT_GENERATION = auto()  # Generate content
    VALIDATION = auto()          # Validate inputs/outputs


@dataclass
class ExecutionContext:
    """Execution context for tool runs."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: str = "production"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolMetadata:
    """
    Metadata describing tool capabilities and configuration.
    
    Attributes:
        name: Unique tool identifier
        version: Tool version string
        description: Human-readable tool description
        supported_operations: List of supported operations
        capabilities: List of tool capabilities
        author: Tool author/maintainer
        license: Tool license information
        dependencies: List of required dependencies
        supported_file_types: List of supported file extensions
        configuration_schema: Optional configuration schema
    """
    name: str
    version: str
    description: str
    supported_operations: List[str] = field(default_factory=list)
    capabilities: List[ToolCapability] = field(default_factory=list)
    author: str = "Unknown"
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=list)
    supported_file_types: List[str] = field(default_factory=list)
    configuration_schema: Optional[Dict[str, Any]] = None


@dataclass
class ToolInput:
    """
    Standardized input structure for tool execution.
    
    Attributes:
        operation: Operation to perform (generate, analyze, validate, etc.)
        target_files: List of target files for operation
        parameters: Operation-specific parameters
        configuration: Tool configuration overrides
        context: Additional execution context
        execution_context: Execution context
        metadata: Input metadata for tracing
    """
    operation: str
    target_files: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    execution_context: Optional[ExecutionContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """
    Standardized result structure for tool execution.
    
    Attributes:
        status: Execution status
        output: Operation results
        output_files: List of files created/modified during execution
        errors: List of errors encountered
        warnings: List of warnings generated
        metrics: Performance and quality metrics
        execution_time: Total execution time in seconds
        metadata: Result metadata for analysis
    """
    status: ToolStatus
    output: Dict[str, Any] = field(default_factory=dict)
    output_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """
    Abstract base class for all development tools.
    
    This class defines the standard interface that all tools must implement
    while providing common functionality for logging, error handling, and
    result processing. All tools inherit from this base class.
    
    Architectural Constraints:
    - Must not import from core modules or other tools
    - Provides standardized interface for tool execution
    - Implements common functionality for all tools
    - Supports configuration and metadata management
    - Thread-safe base implementation
    """
    
    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize base tool with optional configuration.
        
        Args:
            configuration: Optional tool configuration
        """
        self._configuration = configuration or {}
        self._logger = logging.getLogger(self.__class__.__name__)
        self._status = ToolStatus.PENDING
        self._metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """
        Get tool metadata describing capabilities and configuration.
        
        Returns:
            ToolMetadata describing this tool
            
        This method must be implemented by all concrete tools to provide
        accurate metadata about their capabilities and requirements.
        """
        pass
    
    @abstractmethod
    def execute(self, tool_input: ToolInput) -> ToolResult:
        """
        Execute the tool with given input and return results.
        
        Args:
            tool_input: Standardized input for tool execution
            
        Returns:
            ToolResult with execution results and metadata
            
        This is the main execution method that all tools must implement.
        It should handle the core tool functionality while following
        architectural rules and constraints.
        """
        pass
    
    @abstractmethod
    def validate(self, tool_input: ToolInput) -> bool:
        """
        Validate input before execution.
        
        Args:
            tool_input: Input to validate
            
        Returns:
            True if input is valid, False otherwise
            
        This method should validate all aspects of the input including
        file paths, parameters, configuration, and operation types.
        """
        pass
    
    def configure(self, configuration: Dict[str, Any]) -> bool:
        """
        Update tool configuration.
        
        Args:
            configuration: New configuration to apply
            
        Returns:
            True if configuration applied successfully, False otherwise
            
        This method allows runtime configuration updates while maintaining
        tool state consistency and validation.
        """
        try:
            # Validate new configuration
            validation_errors = self._validate_configuration(configuration)
            if validation_errors:
                self._logger.error(f"Configuration validation failed: {validation_errors}")
                return False
            
            # Merge with existing configuration
            self._configuration.update(configuration)
            
            # Log configuration changes
            self._logger.info(f"Configuration updated: {configuration}")
            
            return True
        except Exception as e:
            self._logger.error(f"Failed to update configuration: {str(e)}")
            return False
    
    def get_status(self) -> ToolStatus:
        """
        Get current tool execution status.
        
        Returns:
            Current ToolStatus
        """
        return self._status
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current tool configuration.
        
        Returns:
            Current configuration dictionary
        """
        return self._configuration.copy()
    
    def supports_operation(self, operation: str) -> bool:
        """
        Check if tool supports a specific operation.
        
        Args:
            operation: Operation name to check
            
        Returns:
            True if operation is supported, False otherwise
        """
        return operation in self._metadata.supported_operations
    
    def supports_file_type(self, file_extension: str) -> bool:
        """
        Check if tool supports a specific file type.
        
        Args:
            file_extension: File extension to check (e.g., '.py', '.md')
            
        Returns:
            True if file type is supported, False otherwise
        """
        return file_extension in self._metadata.supported_file_types
    
    def _validate_input(self, tool_input: ToolInput) -> List[str]:
        """
        Private method to validate tool input comprehensively.
        
        Args:
            tool_input: Input to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not tool_input.operation:
            errors.append("Operation is required")
        
        # Check if operation is supported
        if tool_input.operation and not self.supports_operation(tool_input.operation):
            errors.append(f"Operation '{tool_input.operation}' is not supported")
        
        # Validate file paths
        for file_path in tool_input.target_files:
            try:
                Path(file_path)
            except Exception:
                errors.append(f"Invalid file path: {file_path}")
        
        return errors
    
    def _validate_configuration(self, configuration: Dict[str, Any]) -> List[str]:
        """
        Private method to validate configuration.
        
        Args:
            configuration: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation - can be extended by subclasses
        if not isinstance(configuration, dict):
            errors.append("Configuration must be a dictionary")
        
        return errors
    
    def _update_status(self, new_status: ToolStatus) -> None:
        """
        Private method to update tool status with logging.
        
        Args:
            new_status: New status to set
        """
        old_status = self._status
        self._status = new_status
        self._logger.debug(f"Status changed from {old_status} to {new_status}")


# Utility functions for tool management
def create_tool_input(operation: str, **kwargs) -> ToolInput:
    """
    Convenience function to create standardized tool input.
    
    Args:
        operation: Operation to perform
        **kwargs: Additional input parameters
        
    Returns:
        ToolInput with specified parameters
    """
    return ToolInput(operation=operation, **kwargs)


def create_success_result(output: Optional[Dict[str, Any]] = None, **kwargs) -> ToolResult:
    """
    Convenience function to create successful tool result.
    
    Args:
        output: Optional output data
        **kwargs: Additional result parameters
        
    Returns:
        ToolResult indicating success
    """
    return ToolResult(
        status=ToolStatus.SUCCESS,
        output=output or {},
        **kwargs
    )


def create_error_result(errors: List[str], **kwargs) -> ToolResult:
    """
    Convenience function to create error tool result.
    
    Args:
        errors: List of error messages
        **kwargs: Additional result parameters
        
    Returns:
        ToolResult indicating failure
    """
    return ToolResult(
        status=ToolStatus.ERROR,
        errors=errors,
        **kwargs
    )