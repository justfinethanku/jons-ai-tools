"""
@RULE:PURPOSE: General prompt improvement and refinement tool configuration
@RULE:TOOL_TYPE: prompt_processor
@RULE:CATEGORY: content_generation
@RULE:MODEL_PREFERENCE: gemini-2.5-pro-preview-05-06
@RULE:TEMPERATURE: 0.3
@RULE:FALLBACK_MODEL: gpt-4.1-2025-04-14
@RULE:MAX_RETRIES: 3
@RULE:TOP_P: 0.9
@RULE:TOP_K: 40
@RULE:ENABLE_REVISIONS: true
@RULE:ENABLE_EXPLANATIONS: false
@RULE:ENABLE_HISTORY: true
@RULE:MAX_HISTORY_SIZE: 10
@RULE:INPUT_HEIGHT: 120
@RULE:OUTPUT_HEIGHT: 160
@RULE:AUTO_SAVE: false
@RULE:VALIDATION_ENABLED: true
@RULE:BUTTON_TEXT: Refine Prompt
@RULE:SIDEBAR_INFO: This Prompt Refiner helps you iteratively improve your prompts through multiple revisions until you get the perfect result.
@RULE:HELP_TEXT: 1. Enter your rough prompt\n2. Click 'Refine Prompt'\n3. Review the refined version\n4. Ask for revisions if needed\n5. Repeat until perfect!
@RULE:MAX_OUTPUT_TOKENS: 8192
"""

# Tool configuration loaded from rules above
TOOL_CONFIG = {
    'name': 'Prompt Refiner',
    'description': 'Iterative prompt improvement tool',
    'meta_prompt_module': 'prompts.meta_prompts.the_prompt_prompt',
    'supports_revisions': True,
    'supports_explanations': False
}