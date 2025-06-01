"""
@RULE:PURPOSE: Unified tool configuration management with rule-based behavior specification
@RULE:DEPENDENCIES: shared_utils, logging_manager, api_config
@RULE:INTERFACE: get_tool_config, register_tool, validate_tool_config
@RULE:NO_CROSS_TALK: individual tool implementations
"""

from typing import Dict, Any, Optional, Callable, Tuple
from frameworks.shared_utils import extract_string_rules
from frameworks.logging_manager import get_logger
from frameworks.api_config import get_api_config

logger = get_logger("tool_config")

# Tool registry for dynamic tool management
TOOL_REGISTRY = {}

class ToolConfiguration:
    """Unified tool configuration with rule-based behavior specification"""
    
    def __init__(self, tool_name: str, config_rules: Dict[str, Any]):
        self.tool_name = tool_name
        self.config_rules = config_rules
        self._validate_config()
    
    def _validate_config(self):
        """Validate tool configuration rules"""
        required_rules = ['TOOL_TYPE', 'PURPOSE']
        for rule in required_rules:
            if rule not in self.config_rules:
                logger.warning(f"Missing required rule {rule} for tool {self.tool_name}")
    
    def get_api_rules(self) -> Dict[str, Any]:
        """Extract API-specific rules from tool configuration"""
        api_rules = {}
        api_rule_keys = ['MODEL_PREFERENCE', 'TEMPERATURE', 'FALLBACK_MODEL', 'MAX_RETRIES', 'TOP_P', 'TOP_K']
        
        for key in api_rule_keys:
            if key in self.config_rules:
                api_rules[key] = self.config_rules[key]
        
        return api_rules
    
    def get_ui_rules(self) -> Dict[str, Any]:
        """Extract UI-specific rules from tool configuration"""
        ui_rules = {}
        ui_rule_keys = ['INPUT_HEIGHT', 'OUTPUT_HEIGHT', 'ENABLE_REVISIONS', 'ENABLE_EXPLANATIONS', 
                       'SIDEBAR_INFO', 'HELP_TEXT', 'BUTTON_TEXT']
        
        for key in ui_rule_keys:
            if key in self.config_rules:
                ui_rules[key] = self.config_rules[key]
        
        return ui_rules
    
    def get_behavior_rules(self) -> Dict[str, Any]:
        """Extract behavior-specific rules from tool configuration"""
        behavior_rules = {}
        behavior_rule_keys = ['AUTO_SAVE', 'ENABLE_HISTORY', 'MAX_HISTORY_SIZE', 'CLEAR_ON_SUBMIT',
                             'VALIDATION_ENABLED', 'ERROR_HANDLING', 'LOGGING_LEVEL']
        
        for key in behavior_rule_keys:
            if key in self.config_rules:
                behavior_rules[key] = self.config_rules[key]
        
        return behavior_rules

def register_tool(tool_name: str, config_rules: Dict[str, Any], 
                 refine_func: Optional[Callable] = None,
                 revise_func: Optional[Callable] = None,
                 explain_func: Optional[Callable] = None) -> ToolConfiguration:
    """
    Register a tool with unified configuration system.
    
    Args:
        tool_name: Name of the tool
        config_rules: Dictionary of configuration rules
        refine_func: Optional refinement function
        revise_func: Optional revision function  
        explain_func: Optional explanation function
        
    Returns:
        ToolConfiguration instance
    """
    tool_config = ToolConfiguration(tool_name, config_rules)
    
    TOOL_REGISTRY[tool_name] = {
        'config': tool_config,
        'refine_func': refine_func,
        'revise_func': revise_func,
        'explain_func': explain_func
    }
    
    logger.info(f"Tool registered: {tool_name}", 
               tool_type=config_rules.get('TOOL_TYPE', 'unknown'),
               rules_count=len(config_rules))
    
    return tool_config

def get_tool_config(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get tool configuration rules by name"""
    if tool_name in TOOL_REGISTRY:
        return TOOL_REGISTRY[tool_name]['config'].config_rules
    
    # Try to load from config file
    config_file_path = f"tools/configs/{tool_name}_config.py"
    try:
        config_rules = load_tool_config_from_file(config_file_path)
        if config_rules:
            # Register the tool with loaded config
            tool_config = ToolConfiguration(tool_name, config_rules)
            TOOL_REGISTRY[tool_name] = {
                'config': tool_config,
                'refine_func': None,
                'revise_func': None,
                'explain_func': None
            }
            return config_rules
    except Exception as e:
        logger.warning(f"Could not load config for {tool_name}", error=str(e))
    
    return None

def get_tool_function(tool_name: str, function_type: str) -> Optional[Callable]:
    """
    Get tool function by name and type.
    
    Args:
        tool_name: Name of the tool
        function_type: Type of function ('refine', 'revise', 'explain')
        
    Returns:
        Function or None if not found
    """
    if tool_name in TOOL_REGISTRY:
        return TOOL_REGISTRY[tool_name].get(f'{function_type}_func')
    return None

def load_tool_config_from_file(file_path: str) -> Dict[str, Any]:
    """Load tool configuration rules from file comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        success, rules = extract_string_rules(content)
        if success:
            logger.debug(f"Loaded tool config from {file_path}", rules_count=len(rules))
            return rules
        else:
            logger.warning(f"Failed to load tool config from {file_path}")
            return {}
            
    except Exception as e:
        logger.error(f"Error loading tool config from {file_path}", error=str(e))
        return {}

def create_unified_tool_instance(tool_name: str, meta_prompt: str, 
                                config_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a unified tool instance with standardized configuration.
    
    Args:
        tool_name: Name of the tool
        meta_prompt: Meta prompt for the tool
        config_rules: Optional configuration rules override
        
    Returns:
        Dictionary with tool instance configuration
    """
    from frameworks.universal_framework import call_gemini_api, call_openai_api
    
    # Get or create tool configuration
    if config_rules:
        tool_config = ToolConfiguration(tool_name, config_rules)
    else:
        tool_config = get_tool_config(tool_name)
        if not tool_config:
            # Create default configuration
            default_rules = {
                'TOOL_TYPE': 'prompt_processor',
                'PURPOSE': f'{tool_name} prompt processing',
                'MODEL_PREFERENCE': 'gemini-2.5-pro-preview-05-06',
                'TEMPERATURE': 0.3,
                'MAX_RETRIES': 3,
                'ENABLE_REVISIONS': True,
                'ENABLE_HISTORY': True
            }
            tool_config = ToolConfiguration(tool_name, default_rules)
    
    def refine_prompt_unified(rough_prompt: str) -> str:
        """Unified prompt refinement function"""
        api_rules = tool_config.get_api_rules()
        final_prompt = f"{meta_prompt}\n\n[ {rough_prompt} ]"
        
        logger.log_operation_start("unified_refine", tool=tool_name)
        
        try:
            response = call_gemini_api(final_prompt, context_rules=api_rules)
            if response and not response.startswith('Error:'):
                logger.log_operation_success("unified_refine", tool=tool_name)
                return response.strip()
            else:
                logger.log_operation_failure("unified_refine", response or "Empty response", tool=tool_name)
                return response or "Error: Empty response"
        except Exception as e:
            logger.log_operation_failure("unified_refine", str(e), tool=tool_name)
            return f"Error: {str(e)}"
    
    def revise_prompt_unified(current_prompt: str, revision_request: str) -> str:
        """Unified prompt revision function"""
        api_rules = tool_config.get_api_rules()
        # Increase temperature slightly for revision creativity
        revision_rules = api_rules.copy()
        revision_rules['TEMPERATURE'] = min(api_rules.get('TEMPERATURE', 0.3) + 0.2, 1.0)
        
        revision_template = """
You are an expert prompt engineer specializing in prompt revisions.

Your task: Modify the current prompt based on the user's specific feedback, keeping what works well and improving only what they've requested.

CURRENT PROMPT:
{current_prompt}

USER'S REVISION REQUEST:
{revision_request}

INSTRUCTIONS:
- Keep the core structure and good elements
- Focus only on the specific changes requested
- Don't over-engineer - make targeted improvements
- Maintain the original intent while incorporating the feedback
- Return ONLY the revised prompt, no explanation

REVISED PROMPT:
"""
        
        final_prompt = revision_template.format(
            current_prompt=current_prompt,
            revision_request=revision_request
        )
        
        logger.log_operation_start("unified_revise", tool=tool_name)
        
        try:
            response = call_gemini_api(final_prompt, context_rules=revision_rules)
            if response and not response.startswith('Error:'):
                logger.log_operation_success("unified_revise", tool=tool_name)
                return response.strip()
            else:
                logger.log_operation_failure("unified_revise", response or "Empty response", tool=tool_name)
                return response or "Error: Empty response"
        except Exception as e:
            logger.log_operation_failure("unified_revise", str(e), tool=tool_name)
            return f"Error: {str(e)}"
    
    return {
        'config': tool_config,
        'refine_func': refine_prompt_unified,
        'revise_func': revise_prompt_unified,
        'meta_prompt': meta_prompt,
        'tool_name': tool_name
    }

def validate_tool_config(config_rules: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate tool configuration rules.
    
    Args:
        config_rules: Configuration rules to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required rules
        required_rules = ['TOOL_TYPE', 'PURPOSE']
        for rule in required_rules:
            if rule not in config_rules:
                return False, f"Missing required rule: {rule}"
        
        # Validate temperature range
        if 'TEMPERATURE' in config_rules:
            temp = config_rules['TEMPERATURE']
            if not isinstance(temp, (int, float)) or not 0 <= temp <= 2:
                return False, f"Temperature {temp} must be between 0 and 2"
        
        # Validate boolean rules
        boolean_rules = ['ENABLE_REVISIONS', 'ENABLE_EXPLANATIONS', 'AUTO_SAVE', 'ENABLE_HISTORY']
        for rule in boolean_rules:
            if rule in config_rules:
                value = config_rules[rule]
                if not isinstance(value, bool):
                    return False, f"Rule {rule} must be boolean, got {type(value)}"
        
        # Validate integer rules
        integer_rules = ['MAX_RETRIES', 'INPUT_HEIGHT', 'OUTPUT_HEIGHT', 'MAX_HISTORY_SIZE']
        for rule in integer_rules:
            if rule in config_rules:
                value = config_rules[rule]
                if not isinstance(value, int) or value < 0:
                    return False, f"Rule {rule} must be non-negative integer, got {value}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def get_all_registered_tools() -> Dict[str, ToolConfiguration]:
    """Get all registered tool configurations"""
    return {name: registry['config'] for name, registry in TOOL_REGISTRY.items()}

def log_tool_configuration(tool_name: str, config: ToolConfiguration):
    """Log tool configuration for debugging and monitoring"""
    logger.info("Tool configuration loaded",
                tool=tool_name,
                tool_type=config.config_rules.get('TOOL_TYPE'),
                api_rules_count=len(config.get_api_rules()),
                ui_rules_count=len(config.get_ui_rules()),
                behavior_rules_count=len(config.get_behavior_rules()))