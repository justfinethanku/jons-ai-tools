"""
@RULE:LAYER: tools/social_copy_tool
@RULE:FORBIDDEN: core.*, main, streamlit, frameworks.*
@SEE: tools/CLAUDE.md#base-tool-patterns
Social media copy generation tool with platform-specific rules
"""

# Allowed imports
import logging
import time
import os
import importlib
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import from base tool layer
from .base_tool import (
    BaseTool, ToolMetadata, ToolInput, ToolResult, ToolStatus,
    ToolCapability, create_success_result, create_error_result
)

# Import from shared layer
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.ai_client import AIClient, AIRequest, RequestType


# Built-in platform prompts for social media copy generation
FACEBOOK_PROMPT = """Create engaging Facebook copy for the following content. Focus on storytelling, community building, and encouraging meaningful conversations. Use a conversational tone that feels personal and authentic.

Content to adapt: {USER_INPUT}

Requirements:
- Write compelling copy that encourages engagement
- Use natural, conversational language
- Include a clear call-to-action
- Keep it scannable with short paragraphs
- Make it shareable and discussion-worthy"""

LINKEDIN_PROMPT = """Create professional LinkedIn copy for the following content. Focus on business value, professional insights, and industry relevance. Use a tone that's professional yet approachable.

Content to adapt: {USER_INPUT}

Requirements:
- Maintain professional tone while being engaging
- Lead with value or insight
- Include relevant industry context
- Use clear, benefit-focused language
- End with a professional call-to-action"""

TWITTER_PROMPT = """Create concise Twitter copy for the following content. Focus on brevity, impact, and engagement. Use punchy language that captures attention in a crowded feed.

Content to adapt: {USER_INPUT}

Requirements:
- Keep it under 280 characters
- Use strong, action-oriented language
- Make every word count
- Include relevant hashtags strategically
- Create urgency or curiosity"""

INSTAGRAM_PROMPT = """Create visual-focused Instagram copy for the following content. Focus on lifestyle, emotion, and visual storytelling. Use a tone that's authentic and aspirational.

Content to adapt: {USER_INPUT}

Requirements:
- Write copy that complements visuals
- Use emotion-driven language
- Include strategic hashtags
- Create FOMO or aspiration
- Encourage saves and shares"""

TIKTOK_PROMPT = """Create engaging TikTok copy for the following content. Focus on trends, entertainment, and quick hooks. Use casual, energetic language that resonates with younger audiences.

Content to adapt: {USER_INPUT}

Requirements:
- Start with a strong hook
- Use trending language and references
- Keep it entertaining and energetic
- Include relevant hashtags
- Create shareability"""

YOUTUBE_PROMPT = """Create compelling YouTube copy for the following content. Focus on detailed descriptions, SEO optimization, and viewer engagement. Use clear, descriptive language.

Content to adapt: {USER_INPUT}

Requirements:
- Create detailed, SEO-friendly descriptions
- Include clear value proposition
- Use keyword-rich language
- Add clear calls-to-action
- Structure for readability"""

# Default platform rules
DEFAULT_PLATFORM_RULES = {
    "Facebook": {
        "CHARACTER_LIMIT": 2000,
        "HASHTAG_COUNT": {"min": 1, "max": 3},
        "EMOJI_ALLOWED": True,
        "REQUIRED_CTA": True,
        "TONE_STYLE": "conversational and community-focused"
    },
    "LinkedIn": {
        "CHARACTER_LIMIT": 3000,
        "HASHTAG_COUNT": {"min": 3, "max": 5},
        "EMOJI_ALLOWED": False,
        "REQUIRED_CTA": True,
        "TONE_STYLE": "professional yet approachable"
    },
    "Twitter": {
        "CHARACTER_LIMIT": 280,
        "HASHTAG_COUNT": {"min": 1, "max": 3},
        "EMOJI_ALLOWED": True,
        "REQUIRED_CTA": False,
        "TONE_STYLE": "punchy and engaging"
    },
    "Instagram": {
        "CHARACTER_LIMIT": 2200,
        "HASHTAG_COUNT": {"min": 5, "max": 15},
        "EMOJI_ALLOWED": True,
        "REQUIRED_CTA": True,
        "TONE_STYLE": "authentic and aspirational"
    },
    "TikTok": {
        "CHARACTER_LIMIT": 2200,
        "HASHTAG_COUNT": {"min": 3, "max": 8},
        "EMOJI_ALLOWED": True,
        "REQUIRED_CTA": True,
        "TONE_STYLE": "casual and energetic"
    },
    "YouTube": {
        "CHARACTER_LIMIT": 5000,
        "HASHTAG_COUNT": {"min": 3, "max": 15},
        "EMOJI_ALLOWED": True,
        "REQUIRED_CTA": True,
        "TONE_STYLE": "descriptive and SEO-focused"
    }
}

# Built-in platform prompts
PLATFORM_PROMPTS = {
    "Facebook": FACEBOOK_PROMPT,
    "LinkedIn": LINKEDIN_PROMPT,
    "Twitter": TWITTER_PROMPT,
    "Instagram": INSTAGRAM_PROMPT,
    "TikTok": TIKTOK_PROMPT,
    "YouTube": YOUTUBE_PROMPT
}


class SocialCopyTool(BaseTool):
    """
    Tool for generating social media copy across multiple platforms.
    
    This tool takes content and generates platform-optimized social media copy
    for different platforms like Facebook, LinkedIn, Twitter, Instagram, TikTok,
    and YouTube. It applies platform-specific rules and constraints.
    
    Architectural Constraints:
    - Uses shared AI client for LLM interactions
    - Stateless operations for thread safety
    - No UI framework dependencies
    - Standard BaseTool interface
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize social copy tool.
        
        Args:
            ai_client: AI client for making copy generation requests
            configuration: Optional tool configuration
        """
        super().__init__(configuration)
        self._ai_client = ai_client
        
        # Default configuration
        self._default_config = {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1500,
            'timeout': 30,
            'platforms': ['Facebook', 'LinkedIn', 'Twitter', 'Instagram', 'TikTok', 'YouTube']
        }
        
        # Merge with provided configuration
        self._config = {**self._default_config, **self._configuration}
        
        # Load platform prompts and rules
        self._platform_prompts = PLATFORM_PROMPTS.copy()
        self._platform_rules = DEFAULT_PLATFORM_RULES.copy()
        
        # Try to load custom prompts and rules from files
        self._load_external_prompts()
    
    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name="social_copy_tool",
            version="1.0.0",
            description="AI-powered social media copy generation tool with platform-specific optimization",
            supported_operations=["generate", "generate_single", "list_platforms"],
            capabilities=[
                ToolCapability.AI_INTEGRATION,
                ToolCapability.TEXT_PROCESSING,
                ToolCapability.CONTENT_GENERATION,
                ToolCapability.RULE_PROCESSING
            ],
            dependencies=["ai_client"],
            supported_file_types=[".txt", ".md"],
            author="Rebuild Framework"
        )
    
    def validate(self, tool_input: ToolInput) -> bool:
        """
        Validate tool input.
        
        Args:
            tool_input: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Use base validation
        base_errors = self._validate_input(tool_input)
        if base_errors:
            return False
        
        # Check specific requirements
        if tool_input.operation == "generate":
            if "content" not in tool_input.parameters:
                return False
        elif tool_input.operation == "generate_single":
            if "content" not in tool_input.parameters or "platform" not in tool_input.parameters:
                return False
            # Check if platform is supported
            platform = tool_input.parameters["platform"]
            if platform not in self._platform_prompts:
                return False
        elif tool_input.operation == "list_platforms":
            # No additional validation needed
            pass
        else:
            return False
        
        # Check AI client availability
        if not self._ai_client:
            return False
        
        return True
    
    def execute(self, tool_input: ToolInput) -> ToolResult:
        """
        Execute social copy generation operation.
        
        Args:
            tool_input: Standardized tool input
            
        Returns:
            ToolResult with copy generation results
        """
        start_time = time.time()
        self._update_status(ToolStatus.RUNNING)
        
        try:
            # Validate input
            if not self.validate(tool_input):
                return create_error_result(
                    errors=["Invalid input for social copy generation"],
                    execution_time=time.time() - start_time
                )
            
            # Execute based on operation
            if tool_input.operation == "generate":
                result = self._generate_all_platforms(tool_input)
            elif tool_input.operation == "generate_single":
                result = self._generate_single_platform(tool_input)
            elif tool_input.operation == "list_platforms":
                result = self._list_platforms(tool_input)
            else:
                return create_error_result(
                    errors=[f"Unsupported operation: {tool_input.operation}"],
                    execution_time=time.time() - start_time
                )
            
            # Add execution time
            result.execution_time = time.time() - start_time
            self._update_status(ToolStatus.SUCCESS if result.status == ToolStatus.SUCCESS else ToolStatus.ERROR)
            
            return result
            
        except Exception as e:
            self._update_status(ToolStatus.ERROR)
            return create_error_result(
                errors=[f"Execution failed: {str(e)}"],
                execution_time=time.time() - start_time
            )
    
    def _generate_all_platforms(self, tool_input: ToolInput) -> ToolResult:
        """
        Generate copy for all platforms.
        
        Args:
            tool_input: Tool input with content to convert
            
        Returns:
            ToolResult with copy for all platforms
        """
        try:
            content = tool_input.parameters["content"]
            platforms = tool_input.parameters.get("platforms", self._config["platforms"])
            client_data = tool_input.parameters.get("client_data")
            
            results = {}
            total_tokens = 0
            total_response_time = 0.0
            
            # Generate for each platform
            for platform in platforms:
                if platform not in self._platform_prompts:
                    continue
                
                platform_result = self._generate_for_platform(
                    platform, content, client_data, tool_input.configuration
                )
                
                if platform_result["success"]:
                    results[platform] = platform_result["copy"]
                    total_tokens += platform_result.get("tokens", 0)
                    total_response_time += platform_result.get("response_time", 0)
                else:
                    results[platform] = f"Error: {platform_result['error']}"
            
            return create_success_result(
                output={
                    "platform_copy": results,
                    "platforms_generated": len([p for p in results if not results[p].startswith("Error:")]),
                    "total_platforms": len(platforms)
                },
                metrics={
                    "total_tokens": total_tokens,
                    "total_response_time": total_response_time,
                    "platforms_processed": len(platforms)
                }
            )
            
        except Exception as e:
            return create_error_result(
                errors=[f"All platforms generation failed: {str(e)}"]
            )
    
    def _generate_single_platform(self, tool_input: ToolInput) -> ToolResult:
        """
        Generate copy for a single platform.
        
        Args:
            tool_input: Tool input with content and platform
            
        Returns:
            ToolResult with copy for specified platform
        """
        try:
            content = tool_input.parameters["content"]
            platform = tool_input.parameters["platform"]
            client_data = tool_input.parameters.get("client_data")
            
            platform_result = self._generate_for_platform(
                platform, content, client_data, tool_input.configuration
            )
            
            if platform_result["success"]:
                return create_success_result(
                    output={
                        "platform": platform,
                        "copy": platform_result["copy"],
                        "rules_applied": platform_result.get("rules_applied", {}),
                        "model_used": platform_result.get("model_used", "")
                    },
                    metrics={
                        "tokens": platform_result.get("tokens", 0),
                        "response_time": platform_result.get("response_time", 0)
                    }
                )
            else:
                return create_error_result(
                    errors=[f"Single platform generation failed: {platform_result['error']}"]
                )
            
        except Exception as e:
            return create_error_result(
                errors=[f"Single platform generation failed: {str(e)}"]
            )
    
    def _list_platforms(self, tool_input: ToolInput) -> ToolResult:
        """
        List available platforms.
        
        Args:
            tool_input: Tool input (not used)
            
        Returns:
            ToolResult with available platforms
        """
        try:
            return create_success_result(
                output={
                    "platforms": list(self._platform_prompts.keys()),
                    "platform_rules": self._platform_rules
                }
            )
            
        except Exception as e:
            return create_error_result(
                errors=[f"Platform listing failed: {str(e)}"]
            )
    
    def _generate_for_platform(self, platform: str, content: str, client_data: Optional[Dict], 
                             config_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate copy for a specific platform.
        
        Args:
            platform: Platform name
            content: Content to convert
            client_data: Optional client context data
            config_overrides: Configuration overrides
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Get platform prompt and rules
            prompt_template = self._platform_prompts.get(platform, "")
            platform_rules = self._platform_rules.get(platform, {})
            
            if not prompt_template:
                return {"success": False, "error": f"No prompt template for platform: {platform}"}
            
            # Replace content placeholder
            final_prompt = prompt_template.replace("{USER_INPUT}", content)
            
            # Apply platform rules to prompt
            final_prompt = self._apply_platform_rules(final_prompt, platform_rules)
            
            # Add client context if provided
            if client_data:
                client_context = self._format_client_context(client_data)
                final_prompt = client_context + final_prompt
            
            # Create AI request
            ai_request = AIRequest(
                request_type=RequestType.CHAT,
                prompt=final_prompt,
                model=config_overrides.get("model", self._config["model"]),
                temperature=config_overrides.get("temperature", self._config["temperature"]),
                max_tokens=config_overrides.get("max_tokens", self._config["max_tokens"])
            )
            
            # Make AI request
            ai_response = self._ai_client.make_request(ai_request)
            
            if not ai_response.success:
                return {"success": False, "error": ai_response.error_message}
            
            return {
                "success": True,
                "copy": ai_response.content.strip(),
                "rules_applied": platform_rules,
                "model_used": ai_response.model_used,
                "tokens": ai_response.usage.get("total_tokens", 0),
                "response_time": ai_response.response_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_platform_rules(self, prompt: str, platform_rules: Dict[str, Any]) -> str:
        """
        Apply platform-specific rules to the prompt.
        
        Args:
            prompt: Base prompt
            platform_rules: Platform rules to apply
            
        Returns:
            Enhanced prompt with rules
        """
        if not platform_rules:
            return prompt
        
        rule_constraints = []
        
        # Apply character limit
        if "CHARACTER_LIMIT" in platform_rules:
            rule_constraints.append(f"- STRICT CHARACTER LIMIT: {platform_rules['CHARACTER_LIMIT']} characters maximum")
        
        # Apply hashtag requirements
        if "HASHTAG_COUNT" in platform_rules:
            hashtag_info = platform_rules["HASHTAG_COUNT"]
            if isinstance(hashtag_info, dict):
                rule_constraints.append(f"- HASHTAGS: Use {hashtag_info['min']}-{hashtag_info['max']} hashtags")
            else:
                rule_constraints.append(f"- HASHTAGS: Use {hashtag_info} hashtags")
        
        # Apply emoji rules
        if "EMOJI_ALLOWED" in platform_rules and not platform_rules["EMOJI_ALLOWED"]:
            rule_constraints.append("- NO EMOJIS allowed")
        
        # Apply CTA requirements
        if "REQUIRED_CTA" in platform_rules and platform_rules["REQUIRED_CTA"]:
            rule_constraints.append("- MUST include a clear call-to-action")
        
        # Apply tone style
        if "TONE_STYLE" in platform_rules:
            rule_constraints.append(f"- TONE: {platform_rules['TONE_STYLE']}")
        
        if rule_constraints:
            constraints_text = "\n".join(rule_constraints)
            enhanced_prompt = f"""PLATFORM RULES (MUST BE FOLLOWED EXACTLY):
{constraints_text}

{prompt}

REMINDER: Follow all platform rules above exactly. Character limits are strict."""
            return enhanced_prompt
        
        return prompt
    
    def _format_client_context(self, client_data: Dict[str, Any]) -> str:
        """
        Format client context for inclusion in prompts.
        
        Args:
            client_data: Client context data
            
        Returns:
            Formatted client context string
        """
        return f"""CLIENT CONTEXT:
- Client: {client_data.get('name', 'Unknown')}
- Brand Voice: {client_data.get('brand_voice', 'Professional')}
- Tone: {client_data.get('tone', 'Neutral')}
- Industry: {client_data.get('industry', 'General')}

IMPORTANT: Follow the client's brand voice and tone exactly.

"""
    
    def _load_external_prompts(self):
        """
        Load external prompts and rules from files if available.
        
        This attempts to load prompts from the original prompts directory
        structure for backward compatibility.
        """
        try:
            # Try to load from original location
            prompts_dir = Path(__file__).parent.parent.parent / "prompts" / "copy_prompts" / "social_prompts"
            
            if prompts_dir.exists():
                for file_path in prompts_dir.glob("*.py"):
                    if file_path.name.startswith("__"):
                        continue
                    
                    platform_name = file_path.stem.replace("_copy", "").replace("_", " ").title()
                    
                    try:
                        # Read and execute the file to get PROMPT
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        # Extract PROMPT variable if it exists
                        if "PROMPT=" in file_content or "PROMPT =" in file_content:
                            # Simple extraction - could be enhanced
                            exec_globals = {}
                            exec(file_content, exec_globals)
                            if "PROMPT" in exec_globals:
                                self._platform_prompts[platform_name] = exec_globals["PROMPT"]
                        
                        # Extract rules from file content
                        rules = self._extract_rules_from_content(file_content)
                        if rules:
                            self._platform_rules[platform_name] = rules
                            
                    except Exception as e:
                        self._logger.warning(f"Failed to load external prompt for {platform_name}: {str(e)}")
                        
        except Exception as e:
            self._logger.warning(f"Failed to load external prompts: {str(e)}")
    
    def _extract_rules_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract rules from file content.
        
        Args:
            content: File content to parse
            
        Returns:
            Dictionary of extracted rules
        """
        rules = {}
        
        # Simple rule extraction based on @RULE: comments
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('@RULE:') or line.startswith('# @RULE:'):
                # Extract rule name and value
                rule_part = line.replace('@RULE:', '').replace('# @RULE:', '').strip()
                if ':' in rule_part:
                    rule_name, rule_value = rule_part.split(':', 1)
                    rule_name = rule_name.strip()
                    rule_value = rule_value.strip()
                    
                    # Try to parse rule value as appropriate type
                    try:
                        # Try to evaluate as Python literal
                        import ast
                        rules[rule_name] = ast.literal_eval(rule_value)
                    except:
                        # Keep as string
                        rules[rule_name] = rule_value
        
        return rules


# Convenience functions for common operations
def generate_social_copy(ai_client: AIClient, content: str, platforms: Optional[List[str]] = None, **kwargs) -> Dict[str, str]:
    """
    Convenience function to generate social copy for multiple platforms.
    
    Args:
        ai_client: AI client to use
        content: Content to convert to social copy
        platforms: Optional list of platforms to generate for
        **kwargs: Additional configuration
        
    Returns:
        Dictionary mapping platform names to generated copy
    """
    tool = SocialCopyTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="generate",
        parameters={
            "content": content,
            "platforms": platforms
        },
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("platform_copy", {})
    else:
        return {}


def generate_single_platform_copy(ai_client: AIClient, content: str, platform: str, **kwargs) -> str:
    """
    Convenience function to generate copy for a single platform.
    
    Args:
        ai_client: AI client to use
        content: Content to convert
        platform: Platform to generate for
        **kwargs: Additional configuration
        
    Returns:
        Generated copy text
    """
    tool = SocialCopyTool(ai_client=ai_client)
    
    tool_input = ToolInput(
        operation="generate_single",
        parameters={
            "content": content,
            "platform": platform
        },
        configuration=kwargs
    )
    
    result = tool.execute(tool_input)
    
    if result.status == ToolStatus.SUCCESS:
        return result.output.get("copy", "")
    else:
        return ""