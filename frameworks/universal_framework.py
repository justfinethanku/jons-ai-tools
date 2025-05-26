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

# Create structured logger
logger = get_logger("universal_framework")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Client selection is now handled by unified_client_manager

def client_selection_sidebar():
    """Wrapper for backward compatibility"""
    from frameworks.unified_client_manager import get_unified_client_manager
    manager = get_unified_client_manager("universal")
    return manager.client_selector_sidebar(allow_new_client=False)

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
    # Add client selection to all tools
    client_selection_sidebar()

def call_openai_api(prompt: str, model: str = "gpt-4.1-2025-04-14", temperature: float = 1.0) -> str:
    """
    Call the OpenAI API with comprehensive error handling.
    
    Args:
        prompt: The prompt to send to OpenAI
        model: The model to use. Defaults to "gpt-4.1-2025-04-14".
        temperature: Controls randomness in generation. Defaults to 1.0.
        
    Returns:
        The response from OpenAI or error message
    """
    try:
        from openai import OpenAI
        import time
        
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        # Configure the client with error handling
        try:
            api_key = st.secrets["openai"]["OPENAI_API_KEY"]
            if not api_key:
                raise ValueError("OpenAI API key not found in secrets")
            client = OpenAI(api_key=api_key)
        except KeyError:
            raise ValueError("OpenAI configuration not found in secrets.toml")
        
        # Make the API call with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Build parameters
                params = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                # Only add temperature if it's not the default
                if temperature != 1.0:
                    params["temperature"] = temperature
                
                response = client.chat.completions.create(**params)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Validate response
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty response from OpenAI")
                
                logger.log_api_call("openai", model, status_code=200, duration_ms=duration_ms)
                return response.choices[0].message.content
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff 
                        continue
                    raise
                elif attempt < max_retries - 1:
                    logger.error("OpenAI API error", attempt=attempt + 1, error=str(e), model=model)
                    time.sleep(1)  # Brief pause before retry 
                    continue
                else:
                    raise
    
    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        logger.log_api_call("openai", model, status_code=500, error=str(e))
        st.error(error_msg)
        return f"Error: Unable to get response from OpenAI. Please try again."

def call_gemini_api(prompt: str, response_schema: Optional[Dict] = None, temperature: float = 0.2) -> str:
    """
    Call Gemini API with comprehensive error handling and structured output support.   
    
    Args:
        prompt: The prompt to send to Gemini
        response_schema: Schema for structured output  
        temperature: Controls randomness in generation
        
    Returns:
        The response from Gemini or error message
    """
    try:
        import google.generativeai as genai
        import json
        from google.api_core import exceptions
        
        # Validate inputs
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        # Configure the Gemini API client with error handling
        try:
            api_key = st.secrets["google"]["GEMINI_API_KEY"]
            if not api_key:
                raise ValueError("Gemini API key not found in secrets")
            genai.configure(api_key=api_key)
        except KeyError:
            raise ValueError("Google configuration not found in secrets.toml")
        
        # Create generation config
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        # Add response schema if provided
        if response_schema:
            generation_config["response_schema"] = response_schema
            generation_config["response_mime_type"] = "application/json"
        
        # Create the model with error handling
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-pro-preview-05-06",
                generation_config=generation_config
            )
        except Exception as e:
            raise ValueError(f"Failed to create Gemini model: {str(e)}")
        
        # Generate content with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                import time
                start_time = time.time()
                
                response = model.generate_content(prompt)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Validate response
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Empty or invalid response from Gemini")
                
                logger.log_api_call("gemini", "gemini-2.5-pro-preview-05-06", status_code=200, duration_ms=duration_ms)
                
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
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            except exceptions.GoogleAPIError as e:
                logger.error("Gemini API error", attempt=attempt + 1, error=str(e), model="gemini-2.0-flash")
                if attempt < max_retries - 1:
                    continue
                raise
    
    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        logger.log_api_call("gemini", "gemini-2.0-flash", status_code=500, error=str(e))
        st.error(error_msg)
        return f"Error: Unable to get response from Gemini. Please try again."