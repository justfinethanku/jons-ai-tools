"""
@RULE:PURPOSE: Code-focused prompt optimization and technical assistance tool configuration
@RULE:TOOL_TYPE: prompt_processor
@RULE:CATEGORY: development
@RULE:MODEL_PREFERENCE: gemini-2.5-pro-preview-05-06
@RULE:TEMPERATURE: 0.2
@RULE:FALLBACK_MODEL: gpt-4.1-2025-04-14
@RULE:MAX_RETRIES: 3
@RULE:TOP_P: 0.85
@RULE:TOP_K: 30
@RULE:ENABLE_REVISIONS: true
@RULE:ENABLE_EXPLANATIONS: true
@RULE:ENABLE_HISTORY: true
@RULE:MAX_HISTORY_SIZE: 15
@RULE:INPUT_HEIGHT: 120
@RULE:OUTPUT_HEIGHT: 160
@RULE:AUTO_SAVE: false
@RULE:VALIDATION_ENABLED: true
@RULE:BUTTON_TEXT: Refine Prompt
@RULE:SIDEBAR_INFO: This Prompt Refiner helps you improve your initial prompt by making it clearer, more specific, or better structured for coding tasks.
@RULE:HELP_TEXT: - Enter your rough prompt.\n- Click 'Refine Prompt'.\n- Optionally, click 'Explain this' for an explanation.
"""

# Tool configuration loaded from rules above
TOOL_CONFIG = {
    'name': 'Coder Helper',
    'description': 'Code-focused prompt refinement tool',
    'meta_prompt_module': 'prompts.meta_prompts.code_prompt',
    'explainer_prompt_module': 'prompts.meta_prompts.explainer',
    'supports_revisions': True,
    'supports_explanations': True
}