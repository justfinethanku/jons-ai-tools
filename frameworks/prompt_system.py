"""
Hybrid Prompt System - Approach 5 Implementation
Provides both convenience (pre-registered prompts) and flexibility (custom building)
"""

import os
import importlib.util
from typing import List, Dict, Any, Optional
import json


class PromptValidationError(Exception):
    """Raised when prompt validation fails"""
    pass


class StructuredPromptBuilder:
    """Builds 5W structured prompts with mandatory completeness validation"""
    
    REQUIRED_COMPONENTS = ['who', 'what', 'how', 'why', 'format']
    
    def __init__(self, components_path: str = None):
        self.components_path = components_path or "prompts/structured/components"
        self._component_cache = {}
    
    def build(self, components: List[str], **variables) -> str:
        """
        Build a structured prompt from component specifications
        
        Args:
            components: List of component specs like ["who.business_analyst", "what.extract_data"]
            **variables: Variables to substitute in the final prompt
            
        Returns:
            Assembled prompt string
            
        Raises:
            PromptValidationError: If required components are missing
        """
        parsed_components = self._parse_components(components)
        self._validate_5w_completeness(parsed_components)
        
        # Load component content
        content_parts = []
        for category in self.REQUIRED_COMPONENTS:
            if category in parsed_components:
                component_name = parsed_components[category]
                content = self._load_component(category, component_name)
                content_parts.append(content)
        
        # Assemble with natural flow and clean prefixes
        assembled = self._assemble_natural_flow(content_parts)
        cleaned = self._clean_prefixes(assembled)
        
        return cleaned.format(**variables)
    
    def _parse_components(self, components: List[str]) -> Dict[str, str]:
        """Parse component specs into category -> name mapping"""
        parsed = {}
        for component_spec in components:
            if '.' not in component_spec:
                raise PromptValidationError(f"Invalid component spec: {component_spec}. Expected format: 'category.name'")
            
            category, name = component_spec.split('.', 1)
            if category in parsed:
                raise PromptValidationError(f"Duplicate component category: {category}")
            
            parsed[category] = name
        
        return parsed
    
    def _validate_5w_completeness(self, components: Dict[str, str]):
        """Ensure all 5W components are present"""
        missing = set(self.REQUIRED_COMPONENTS) - set(components.keys())
        if missing:
            raise PromptValidationError(f"Missing required components: {missing}")
    
    def _load_component(self, category: str, name: str) -> str:
        """Load component content from file"""
        cache_key = f"{category}.{name}"
        if cache_key in self._component_cache:
            return self._component_cache[cache_key]
        
        component_filename = f"{category}_{name}.py"
        component_path = os.path.join(self.components_path, component_filename)
        
        if not os.path.exists(component_path):
            raise PromptValidationError(f"Component file not found: {component_path}")
        
        spec = importlib.util.spec_from_file_location("component", component_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'CONTENT'):
            raise PromptValidationError(f"Component {component_filename} missing CONTENT attribute")
        
        content = module.CONTENT
        self._component_cache[cache_key] = content
        return content
    
    def _assemble_natural_flow(self, content_parts: List[str]) -> str:
        """Assemble components with natural sentence flow"""
        return "\n\n".join(content_parts)
    
    def _clean_prefixes(self, prompt: str) -> str:
        """Remove WHO:/WHAT:/etc prefixes from final output"""
        import re
        return re.sub(r'^(WHO|WHAT|HOW|WHY|FORMAT):\s*', '', prompt, flags=re.MULTILINE)
    
    def get_missing_components(self, components: List[str]) -> List[str]:
        """Debug helper to see what components are missing"""
        try:
            parsed = self._parse_components(components)
            missing = set(self.REQUIRED_COMPONENTS) - set(parsed.keys())
            return list(missing)
        except PromptValidationError:
            return []


class SimplePromptBuilder:
    """Builds simple template-based prompts for utilities and quick operations"""
    
    def __init__(self, templates_path: str = None):
        self.templates_path = templates_path or "prompts/simple/templates"
        self._template_cache = {}
    
    def build(self, template: str, **variables) -> str:
        """
        Build a simple prompt from template
        
        Args:
            template: Either a template string or template name to load from file
            **variables: Variables to substitute
            
        Returns:
            Completed prompt string
        """
        # If template contains {}, treat as inline template
        if '{' in template and '}' in template:
            return template.format(**variables)
        
        # Otherwise, load from file
        template_content = self._load_template(template)
        return template_content.format(**variables)
    
    def _load_template(self, template_name: str) -> str:
        """Load template from file"""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        template_path = os.path.join(self.templates_path, f"{template_name}.py")
        if not os.path.exists(template_path):
            raise PromptValidationError(f"Template file not found: {template_path}")
        
        spec = importlib.util.spec_from_file_location("template", template_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'CONTENT'):
            raise PromptValidationError(f"Template {template_name} missing CONTENT attribute")
        
        content = module.CONTENT
        self._template_cache[template_name] = content
        return content


class CreativePromptBuilder:
    """Builds flexible creative prompts from mix-and-match components"""
    
    def __init__(self, components_path: str = None):
        self.components_path = components_path or "prompts/creative"
        self._component_cache = {}
    
    def build(self, *component_specs, **variables) -> str:
        """
        Build creative prompt from flexible components
        
        Args:
            *component_specs: Component specs like "starters.imagine_if", "styles.enthusiastic"
            **variables: Variables to substitute
            
        Returns:
            Assembled creative prompt
        """
        content_parts = []
        for spec in component_specs:
            content = self._load_creative_component(spec)
            content_parts.append(content)
        
        assembled = "\n\n".join(content_parts)
        return assembled.format(**variables)
    
    def _load_creative_component(self, component_spec: str) -> str:
        """Load creative component from file"""
        if component_spec in self._component_cache:
            return self._component_cache[component_spec]
        
        if '.' not in component_spec:
            raise PromptValidationError(f"Invalid creative component spec: {component_spec}")
        
        category, name = component_spec.split('.', 1)
        component_path = os.path.join(self.components_path, category, f"{name}.py")
        
        if not os.path.exists(component_path):
            raise PromptValidationError(f"Creative component not found: {component_path}")
        
        spec = importlib.util.spec_from_file_location("component", component_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'CONTENT'):
            raise PromptValidationError(f"Creative component missing CONTENT attribute")
        
        content = module.CONTENT
        self._component_cache[component_spec] = content
        return content


class PromptSystem:
    """
    Main prompt system providing both convenience and flexibility
    """
    
    def __init__(self):
        self.structured = StructuredPromptBuilder()
        self.simple = SimplePromptBuilder()
        self.creative = CreativePromptBuilder()
        self._registry = {}
    
    def register(self, name: str, tier: str, components: List[str], **metadata):
        """
        Register a common prompt pattern for easy reuse
        
        Args:
            name: Prompt name for retrieval
            tier: "structured", "simple", or "creative"
            components: Component specifications
            **metadata: Additional metadata (description, variables, temperature, etc.)
        """
        self._registry[name] = {
            'tier': tier,
            'components': components,
            'metadata': metadata,
            # Extract commonly used metadata for easy access
            'temperature': metadata.get('temperature', 0.7),
            'variables': metadata.get('variables', [])
        }
    
    def get_prompt(self, name: str, **variables) -> str:
        """Get pre-registered prompt by name"""
        if name not in self._registry:
            raise PromptValidationError(f"Prompt '{name}' not found in registry")
        
        config = self._registry[name]
        tier = config['tier']
        components = config['components']
        
        if tier == 'structured':
            return self.structured.build(components, **variables)
        elif tier == 'simple':
            # For simple, components[0] is the template
            return self.simple.build(components[0], **variables)
        elif tier == 'creative':
            return self.creative.build(*components, **variables)
        else:
            raise PromptValidationError(f"Unknown tier: {tier}")
    
    def get_prompt_with_config(self, name: str, **variables) -> tuple[str, dict]:
        """
        Get prompt along with its configuration (temperature, etc.)
        
        Returns:
            tuple: (prompt_string, config_dict)
        """
        if name not in self._registry:
            raise PromptValidationError(f"Prompt '{name}' not found in registry")
        
        config = self._registry[name]
        prompt = self.get_prompt(name, **variables)
        
        return prompt, {
            'temperature': config['temperature'],
            'metadata': config['metadata']
        }
    
    def build_custom(self, tier: str, *components, **variables) -> str:
        """Build custom prompt on the fly"""
        if tier == 'structured':
            return self.structured.build(list(components), **variables)
        elif tier == 'simple':
            return self.simple.build(components[0], **variables)
        elif tier == 'creative':
            return self.creative.build(*components, **variables)
        else:
            raise PromptValidationError(f"Unknown tier: {tier}")
    
    def list_registered_prompts(self) -> Dict[str, Dict]:
        """List all registered prompts with metadata"""
        return {name: config['metadata'] for name, config in self._registry.items()}
    
    def validate_prompt_config(self, name: str) -> bool:
        """Validate a registered prompt configuration"""
        if name not in self._registry:
            return False
        
        config = self._registry[name]
        tier = config['tier']
        components = config['components']
        
        try:
            if tier == 'structured':
                # Check if all components exist and 5W is complete
                missing = self.structured.get_missing_components(components)
                return len(missing) == 0
            elif tier in ['simple', 'creative']:
                # Basic existence check for simple/creative
                return len(components) > 0
            return False
        except Exception:
            return False


# Global instance for easy access
prompt_system = PromptSystem()