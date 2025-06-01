"""
@RULE:PURPOSE: Unified tool management system for rule-based tool configuration and execution
@RULE:DEPENDENCIES: tool_config, shared_utils, logging_manager
@RULE:INTERFACE: load_tool, get_tool_instance, execute_tool_function
@RULE:NO_CROSS_TALK: individual tool implementations
"""

import os
import importlib
from typing import Dict, Any, Optional, Callable
from frameworks.tool_config import (
    create_unified_tool_instance, 
    load_tool_config_from_file,
    register_tool,
    get_tool_config,
    get_tool_function,
    validate_tool_config,
    log_tool_configuration
)
from frameworks.shared_utils import extract_string_rules
from frameworks.logging_manager import get_logger

logger = get_logger("unified_tool_manager")

class UnifiedToolManager:
    """Manages all tools with unified rule-based configuration"""
    
    def __init__(self):
        self.loaded_tools = {}
        self.tool_configs = {}
        
    def discover_tool_configs(self, config_dir: str = "tools/configs") -> Dict[str, str]:
        """
        Discover all tool configuration files in the specified directory.
        
        Args:
            config_dir: Directory containing tool configuration files
            
        Returns:
            Dictionary mapping tool names to config file paths
        """
        discovered_configs = {}
        
        try:
            if os.path.exists(config_dir):
                for filename in os.listdir(config_dir):
                    if filename.endswith('_config.py') and not filename.startswith('__'):
                        tool_name = filename.replace('_config.py', '')
                        config_path = os.path.join(config_dir, filename)
                        discovered_configs[tool_name] = config_path
                        logger.debug(f"Discovered tool config: {tool_name} at {config_path}")
            else:
                logger.warning(f"Config directory not found: {config_dir}")
                
        except Exception as e:
            logger.error(f"Error discovering tool configs", error=str(e))
        
        return discovered_configs
    
    def load_tool_config(self, tool_name: str, config_path: str) -> Optional[Dict[str, Any]]:
        """
        Load tool configuration from file.
        
        Args:
            tool_name: Name of the tool
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary or None if failed
        """
        try:
            # Load rules from file comments
            config_rules = load_tool_config_from_file(config_path)
            
            if not config_rules:
                logger.warning(f"No configuration rules found for {tool_name}")
                return None
            
            # Validate configuration
            is_valid, error_msg = validate_tool_config(config_rules)
            if not is_valid:
                logger.error(f"Invalid config for {tool_name}: {error_msg}")
                return None
            
            # Load additional metadata from the config module
            try:
                module_name = f"tools.configs.{tool_name}_config"
                config_module = importlib.import_module(module_name)
                tool_metadata = getattr(config_module, 'TOOL_CONFIG', {})
                
                # Combine rules and metadata
                config_rules.update(tool_metadata)
                
            except ImportError:
                logger.warning(f"Could not load metadata for {tool_name}")
            
            self.tool_configs[tool_name] = config_rules
            logger.info(f"Loaded configuration for {tool_name}", rules_count=len(config_rules))
            
            return config_rules
            
        except Exception as e:
            logger.error(f"Error loading config for {tool_name}", error=str(e))
            return None
    
    def create_tool_instance(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Create a unified tool instance based on configuration.
        
        Args:
            tool_name: Name of the tool to create
            
        Returns:
            Tool instance dictionary or None if failed
        """
        if tool_name not in self.tool_configs:
            logger.error(f"No configuration found for tool: {tool_name}")
            return None
        
        config = self.tool_configs[tool_name]
        
        try:
            # Load meta prompt
            meta_prompt_module = config.get('meta_prompt_module')
            if meta_prompt_module:
                try:
                    prompt_module = importlib.import_module(meta_prompt_module)
                    meta_prompt = getattr(prompt_module, 'PROMPT', '')
                except ImportError:
                    logger.warning(f"Could not load meta prompt for {tool_name}")
                    meta_prompt = "You are a helpful AI assistant."
            else:
                meta_prompt = "You are a helpful AI assistant."
            
            # Create unified tool instance
            tool_instance = create_unified_tool_instance(tool_name, meta_prompt, config)
            
            # Add explanation function if supported
            if config.get('supports_explanations', False):
                explainer_module = config.get('explainer_prompt_module')
                if explainer_module:
                    try:
                        explainer_mod = importlib.import_module(explainer_module)
                        explainer_prompt = getattr(explainer_mod, 'PROMPT', '')
                        
                        def explain_func(refined_prompt: str) -> str:
                            """Unified explanation function"""
                            from frameworks.universal_framework import call_gemini_api
                            
                            api_rules = tool_instance['config'].get_api_rules()
                            explain_rules = api_rules.copy()
                            explain_rules['TEMPERATURE'] = 0.4  # Moderate temp for explanations
                            
                            final_prompt = explainer_prompt.replace("[Insert prompt to be analyzed here]", refined_prompt)
                            
                            try:
                                response = call_gemini_api(final_prompt, context_rules=explain_rules)
                                return response.strip() if response and not response.startswith('Error:') else response
                            except Exception as e:
                                return f"Error: {str(e)}"
                        
                        tool_instance['explain_func'] = explain_func
                        
                    except ImportError:
                        logger.warning(f"Could not load explainer prompt for {tool_name}")
            
            self.loaded_tools[tool_name] = tool_instance
            
            # Register with global tool registry
            register_tool(
                tool_name,
                config,
                tool_instance['refine_func'],
                tool_instance['revise_func'],
                tool_instance.get('explain_func')
            )
            
            log_tool_configuration(tool_name, tool_instance['config'])
            
            logger.info(f"Created tool instance: {tool_name}")
            return tool_instance
            
        except Exception as e:
            logger.error(f"Error creating tool instance for {tool_name}", error=str(e))
            return None
    
    def load_all_tools(self) -> Dict[str, Any]:
        """
        Discover and load all available tools.
        
        Returns:
            Dictionary of loaded tool instances
        """
        logger.log_operation_start("load_all_tools")
        
        # Discover tool configurations
        discovered_configs = self.discover_tool_configs()
        
        loaded_count = 0
        for tool_name, config_path in discovered_configs.items():
            # Load configuration
            config = self.load_tool_config(tool_name, config_path)
            if config:
                # Create tool instance
                instance = self.create_tool_instance(tool_name)
                if instance:
                    loaded_count += 1
        
        logger.log_operation_success("load_all_tools", 
                                   tools_discovered=len(discovered_configs),
                                   tools_loaded=loaded_count)
        
        return self.loaded_tools
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a loaded tool instance by name"""
        return self.loaded_tools.get(tool_name)
    
    def execute_tool_function(self, tool_name: str, function_type: str, *args, **kwargs) -> Any:
        """
        Execute a tool function with unified error handling.
        
        Args:
            tool_name: Name of the tool
            function_type: Type of function ('refine', 'revise', 'explain')
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or error message
        """
        tool_instance = self.get_tool(tool_name)
        if not tool_instance:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        func_key = f"{function_type}_func"
        if func_key not in tool_instance:
            error_msg = f"Function {function_type} not supported by tool {tool_name}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        try:
            logger.log_operation_start(f"execute_{function_type}", tool=tool_name)
            result = tool_instance[func_key](*args, **kwargs)
            logger.log_operation_success(f"execute_{function_type}", tool=tool_name)
            return result
            
        except Exception as e:
            logger.log_operation_failure(f"execute_{function_type}", str(e), tool=tool_name)
            return f"Error: {str(e)}"
    
    def get_tool_configuration(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration rules"""
        return self.tool_configs.get(tool_name)
    
    def list_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with their metadata"""
        tools_info = {}
        for tool_name, instance in self.loaded_tools.items():
            config = instance['config']
            tools_info[tool_name] = {
                'description': instance.get('description', ''),
                'tool_type': config.config_rules.get('TOOL_TYPE'),
                'category': config.config_rules.get('CATEGORY'),
                'supports_revisions': config.config_rules.get('ENABLE_REVISIONS', False),
                'supports_explanations': config.config_rules.get('ENABLE_EXPLANATIONS', False),
                'api_model': config.config_rules.get('MODEL_PREFERENCE'),
                'temperature': config.config_rules.get('TEMPERATURE')
            }
        return tools_info

# Global tool manager instance
_tool_manager = UnifiedToolManager()

def get_unified_tool_manager() -> UnifiedToolManager:
    """Get the global unified tool manager instance"""
    return _tool_manager

def load_all_tools() -> Dict[str, Any]:
    """Convenience function to load all tools"""
    return _tool_manager.load_all_tools()

def get_tool_instance(tool_name: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get a tool instance"""
    return _tool_manager.get_tool(tool_name)

def execute_unified_tool_function(tool_name: str, function_type: str, *args, **kwargs) -> Any:
    """Convenience function to execute a tool function"""
    return _tool_manager.execute_tool_function(tool_name, function_type, *args, **kwargs)