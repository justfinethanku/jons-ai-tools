"""
frameworks/universal_framework 
"""
import streamlit as st
import io
import os
import json
import traceback
from typing import Dict, Any, Optional, Union, Tuple
from frameworks.shared_utils import safe_json_parse, sanitize_text_for_notion
from frameworks.logging_manager import get_logger
from frameworks.api_config import get_api_config, validate_api_params, apply_retry_rules, log_api_configuration

# Create structured logger
logger = get_logger("universal_framework")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Client selection removed - no longer using Notion

def client_selection_sidebar():
    """Removed - no client selection needed"""
    return None

def enhance_prompt_with_client_context(prompt_template: str, client_data: Optional[Dict[str, Any]]) -> str:
    """Enhance a prompt template with client-specific context.
    
    Args:
        prompt_template: The base prompt template
        client_data: Dictionary containing client information
        
    Returns:
        Enhanced prompt with client context
    """
    try:
        if not client_data or not prompt_template:
            return prompt_template or ""
        
        # Add client context to the prompt
        client_context = f"""
# CLIENT CONTEXT
- Client: {client_data.get('name', 'Unknown')}
- Brand Voice: {client_data.get('brand_voice', 'Professional')}
- Tone: {client_data.get('tone', 'Neutral')}
- Industry: {client_data.get('industry', 'General')}
- Target Audience: {client_data.get('target_audience', 'General public')}
"""
        
        if client_data.get('keywords'):
            client_context += f"- Keywords to include: {', '.join(client_data['keywords'])}\n"
        
        if client_data.get('custom_prompts'):
            client_context += f"- Custom Instructions: {client_data['custom_prompts']}\n"
        
        client_context += """
# IMPORTANT INSTRUCTIONS
- Write specifically for the target audience in the specified industry
- Match the brand voice and tone exactly
- Naturally incorporate the keywords when relevant
- Follow any custom instructions provided
- Maintain consistency with the client's brand identity

"""
        
        # Insert client context after the Role section
        if "# Role" in prompt_template:
            parts = prompt_template.split("# Role", 1)
            enhanced_prompt = parts[0] + "# Role" + parts[1].split("\n", 1)[0] + "\n\n" + client_context + "\n".join(parts[1].split("\n")[1:])
        else:
            enhanced_prompt = client_context + prompt_template
    
        return enhanced_prompt
    except Exception as e:
        logger.error("Failed to enhance prompt", error=str(e), client_id=client_data.get('id') if client_data else None)
        st.warning(f"⚠️ Could not apply client context: {str(e)}")
        return prompt_template

def outputs_to_txt_bytes(outputs_dict: Dict[str, str]) -> bytes:
    """Convert outputs dictionary to text bytes with error handling.
    
    Args:
        outputs_dict: Dictionary of output title-content pairs
        
    Returns:
        UTF-8 encoded bytes of formatted text
    """
    try:
        if not outputs_dict:
            return b"No outputs available\n"
        
        output = io.StringIO()
        for title, content in outputs_dict.items():
            safe_title = sanitize_text_for_notion(str(title))
            safe_content = sanitize_text_for_notion(str(content))
            output.write(f"{safe_title}\n")
            output.write("=" * len(safe_title) + "\n")
            output.write(f"{safe_content}\n\n")
        return output.getvalue().encode("utf-8")
    except Exception as e:
        logger.error("Failed to convert outputs to bytes", error=str(e))
        error_msg = f"Error generating output file: {str(e)}\n"
        return error_msg.encode("utf-8")

def home_button(outputs_dict=None, key_prefix="", tool_name=None):
    if st.session_state.get("tool", "home") != "home":
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🏠 ", key=f"{key_prefix}_home_button"):
                st.session_state.tool = "home"
                st.rerun()
        with col2:
            if outputs_dict:
                file_bytes = outputs_to_txt_bytes(outputs_dict)
                from datetime import datetime
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_base = tool_name if tool_name else st.session_state.get("tool", "llm_outputs")
                file_name = f"{file_base}_{now}.txt"
                st.download_button(
                    label="💾 Save Outputs",
                    data=file_bytes,
                    file_name=file_name,
                    mime="text/plain",
                    key=f"{key_prefix}_save_outputs_download"
                )

def universal_ui():
    """Universal elements for all tools"""
    # Client selection removed
    pass

def call_openai_api(prompt: str, model: str = "gpt-4.1-2025-04-14", temperature: float = 1.0, 
                    context_rules: Optional[Dict[str, Any]] = None) -> str:
    """
    Call the OpenAI API with rule-based configuration and comprehensive error handling.
    
    Args:
        prompt: The prompt to send to OpenAI
        model: The model to use. Defaults to "gpt-4.1-2025-04-14".
        temperature: Controls randomness in generation. Defaults to 1.0.
        context_rules: Optional rules from calling context for parameter overrides
        
    Returns:
        The response from OpenAI or error message
    """
    try:
        from openai import OpenAI
        import time
        
        # Get rule-based API configuration
        api_config = get_api_config("openai", context_rules)
        log_api_configuration("openai", api_config, "rule_based" if context_rules else "default")
        
        # Apply rule-based parameter overrides
        effective_model = api_config.get('model', model)
        effective_temperature = api_config.get('temperature', temperature)
        max_tokens = api_config.get('max_tokens', api_config.get('MAX_TOKENS', 4096))
        
        # Validate inputs with rules
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        is_valid, error_msg = validate_api_params("openai", 
                                                 temperature=effective_temperature,
                                                 max_tokens=max_tokens)
        if not is_valid:
            raise ValueError(f"Parameter validation failed: {error_msg}")
        
        # Configure the client with error handling
        try:
            api_key = st.secrets["openai"]["OPENAI_API_KEY"]
            if not api_key:
                raise ValueError("OpenAI API key not found in secrets")
            client = OpenAI(api_key=api_key)
        except KeyError:
            raise ValueError("OpenAI configuration not found in secrets.toml")
        
        # Get retry configuration from rules
        retry_config = apply_retry_rules(api_config)
        logger.info("OpenAI API call starting",
                   model=effective_model, 
                   temperature=effective_temperature,
                   max_retries=retry_config['max_retries'])
        
        # Make the API call with rule-based retry logic
        for attempt in range(retry_config['max_retries']):
            try:
                start_time = time.time()
                
                # Build parameters with rule-based configuration
                params = {
                    "model": effective_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                }
                
                # Only add temperature if it's not the default
                if effective_temperature != 1.0:
                    params["temperature"] = effective_temperature
                
                response = client.chat.completions.create(**params)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Validate response
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty response from OpenAI")
                
                logger.log_api_call("openai", effective_model, status_code=200, duration_ms=duration_ms)
                logger.log_operation_success("openai_api_call", duration_ms=duration_ms, 
                                           model=effective_model, rules_applied=bool(context_rules))
                return response.choices[0].message.content
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    if attempt < retry_config['max_retries'] - 1:
                        delay = retry_config['base_delay'] * (2 ** attempt)  # Rule-based exponential backoff
                        logger.warning(f"Rate limit hit, retrying in {delay}s", attempt=attempt + 1)
                        time.sleep(delay)
                        continue
                    raise
                elif attempt < retry_config['max_retries'] - 1:
                    logger.error("OpenAI API error", attempt=attempt + 1, error=str(e), model=effective_model)
                    time.sleep(retry_config['base_delay'])  # Rule-based retry delay
                    continue
                else:
                    raise
    
    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        effective_model = api_config.get('model', model) if 'api_config' in locals() else model
        logger.log_api_call("openai", effective_model, status_code=500, error=str(e))
        logger.log_operation_failure("openai_api_call", str(e), model=effective_model)
        st.error(error_msg)
        return f"Error: Unable to get response from OpenAI. Please try again."

def call_gemini_api(prompt: str, response_schema: Optional[Dict] = None, temperature: float = 0.2,
                   context_rules: Optional[Dict[str, Any]] = None) -> str:
    """
    Call Gemini API with rule-based configuration and comprehensive error handling.   
    
    Args:
        prompt: The prompt to send to Gemini
        response_schema: Schema for structured output  
        temperature: Controls randomness in generation
        context_rules: Optional rules from calling context for parameter overrides
        
    Returns:
        The response from Gemini or error message
    """
    try:
        import google.generativeai as genai
        import json
        from google.api_core import exceptions
        
        # Get rule-based API configuration
        api_config = get_api_config("gemini", context_rules)
        log_api_configuration("gemini", api_config, "rule_based" if context_rules else "default")
        
        # Apply rule-based parameter overrides
        effective_model = api_config.get('model', api_config.get('DEFAULT_MODEL'))
        effective_temperature = api_config.get('temperature', temperature)
        top_p = api_config.get('top_p', api_config.get('TOP_P', 0.95))
        top_k = api_config.get('top_k', api_config.get('TOP_K', 40))
        max_output_tokens = api_config.get('max_output_tokens', api_config.get('MAX_OUTPUT_TOKENS', 4096))
        
        # Validate inputs with rules
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        is_valid, error_msg = validate_api_params("gemini", 
                                                 temperature=effective_temperature,
                                                 top_p=top_p,
                                                 top_k=top_k)
        if not is_valid:
            raise ValueError(f"Parameter validation failed: {error_msg}")
        
        # Configure the Gemini API client with error handling
        try:
            api_key = st.secrets["google"]["GEMINI_API_KEY"]
            if not api_key:
                raise ValueError("Gemini API key not found in secrets")
            genai.configure(api_key=api_key)
        except KeyError:
            raise ValueError("Google configuration not found in secrets.toml")
        
        # Create rule-based generation config
        generation_config = {
            "temperature": effective_temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
        }
        
        # Add response schema if provided
        if response_schema:
            generation_config["response_schema"] = response_schema
            generation_config["response_mime_type"] = "application/json"
        
        # Create the model with error handling
        try:
            model = genai.GenerativeModel(
                model_name=effective_model,
                generation_config=generation_config
            )
        except Exception as e:
            raise ValueError(f"Failed to create Gemini model: {str(e)}")
        
        # Get retry configuration from rules
        retry_config = apply_retry_rules(api_config)
        logger.info("Gemini API call starting",
                   model=effective_model, 
                   temperature=effective_temperature,
                   max_retries=retry_config['max_retries'])
        
        # Generate content with rule-based retry logic
        for attempt in range(retry_config['max_retries']):
            try:
                import time
                start_time = time.time()
                
                response = model.generate_content(prompt)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Validate response
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Empty or invalid response from Gemini")
                
                logger.log_api_call("gemini", effective_model, status_code=200, duration_ms=duration_ms)
                logger.log_operation_success("gemini_api_call", duration_ms=duration_ms, 
                                           model=effective_model, rules_applied=bool(context_rules))
                
                # Handle structured response
                if response_schema and hasattr(response, 'candidates') and response.candidates:
                    try:
                        if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                            json_text = response.candidates[0].content.parts[0].text
                            # Validate JSON if schema provided
                            if json_text:
                                success, parsed = safe_json_parse(json_text)
                                if success:
                                    return json_text
                            return json_text
                        else:
                            return response.text
                    except Exception as e:
                        logger.warning("Error parsing structured response", error=str(e))
                        return response.text
                else:
                    # Return unstructured response
                    return response.text
                    
            except exceptions.ResourceExhausted:
                if attempt < retry_config['max_retries'] - 1:
                    import time
                    delay = retry_config['base_delay'] * (2 ** attempt)  # Rule-based exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {delay}s", attempt=attempt + 1)
                    time.sleep(delay)
                    continue
                raise
            except exceptions.GoogleAPIError as e:
                logger.error("Gemini API error", attempt=attempt + 1, error=str(e), model=effective_model)
                if attempt < retry_config['max_retries'] - 1:
                    time.sleep(retry_config['base_delay'])  # Rule-based retry delay
                    continue
                raise
    
    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        effective_model = api_config.get('model', api_config.get('DEFAULT_MODEL')) if 'api_config' in locals() else "gemini-2.0-flash"
        logger.log_api_call("gemini", effective_model, status_code=500, error=str(e))
        logger.log_operation_failure("gemini_api_call", str(e), model=effective_model)
        st.error(error_msg)
        return f"Error: Unable to get response from Gemini. Please try again."