import streamlit as st
import os
import importlib
import google.generativeai as genai
import openai
from frameworks.universal_framework import outputs_to_txt_bytes, call_gemini_api, call_openai_api
from frameworks.shared_utils import extract_string_rules
from frameworks.logging_manager import get_logger
from frameworks.tool_config import get_tool_config
from prompts.client_add_ons.legacy_add_on import PROMPT as LEGACY_ADDON_PROMPT

# Initialize logger and load tool configuration
logger = get_logger("social_copy_tool")
tool_config = get_tool_config("social_copy_tool")

def load_all_prompts():
    """Dynamically load all prompts and their rules from social_prompts folder"""
    prompts = {}
    prompt_rules = {}
    base_path = "prompts.copy_prompts.social_prompts"
    
    # Get all .py files in the social_prompts directory
    social_prompts_dir = "prompts/copy_prompts/social_prompts"
    
    try:
        for filename in os.listdir(social_prompts_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                platform_name = filename[:-3]  # Remove .py extension
                try:
                    module_path = f"{base_path}.{platform_name}"
                    module = importlib.import_module(module_path)
                    if hasattr(module, 'PROMPT'):
                        # Format platform name nicely (facebook_copy -> Facebook)
                        display_name = platform_name.replace('_copy', '').replace('_', ' ').title()
                        prompts[display_name] = module.PROMPT
                        
                        # Extract rules from the module file
                        file_path = os.path.join(social_prompts_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        success, rules = extract_string_rules(file_content)
                        if success and rules:
                            prompt_rules[display_name] = rules
                            logger.info(f"Loaded rules for {display_name}", 
                                      platform=display_name, rules_count=len(rules))
                        else:
                            prompt_rules[display_name] = {}
                            
                except ImportError as e:
                    st.error(f"Could not load {platform_name}: {e}")
                except Exception as e:
                    logger.error(f"Error loading rules for {platform_name}", error=str(e))
                    
    except FileNotFoundError:
        st.error(f"Directory not found: {social_prompts_dir}")
    
    return prompts, prompt_rules

def display_rule_summary(prompt_rules):
    """Display a summary of rules being applied"""
    if not prompt_rules:
        return
    
    st.markdown("""
        <div style="background: #1a1a1a; border: 2px solid #0f0; padding: 15px; margin: 20px 0;">
            <p style="font-family: 'Courier New', monospace; color: #0f0; font-size: 20px; 
                      text-align: center; margin: 0 0 15px 0;">
                ⚙️ ACTIVE RULES ENGINE ⚙️
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        for platform_name, rules in prompt_rules.items():
            if rules:
                # Separate content rules from API rules
                content_rules = {}
                api_rules = {}
                
                for rule_name, rule_value in rules.items():
                    if rule_name in ['MODEL_PREFERENCE', 'TEMPERATURE', 'FALLBACK_MODEL', 'MAX_RETRIES', 'TOP_P', 'TOP_K', 'MAX_TOKENS']:
                        api_rules[rule_name] = rule_value
                    else:
                        content_rules[rule_name] = rule_value
                
                with st.expander(f"📋 {platform_name} Rules ({len(rules)} active)", expanded=False):
                    
                    if content_rules:
                        st.markdown("**Content & Format Rules:**")
                        for rule_name, rule_value in content_rules.items():
                            if isinstance(rule_value, dict) and 'min' in rule_value and 'max' in rule_value:
                                st.write(f"• **{rule_name}**: {rule_value['min']}-{rule_value['max']}")
                            elif isinstance(rule_value, list):
                                st.write(f"• **{rule_name}**: {', '.join(map(str, rule_value))}")
                            else:
                                st.write(f"• **{rule_name}**: {rule_value}")
                    
                    if api_rules:
                        st.markdown("**API Configuration Rules:**")
                        for rule_name, rule_value in api_rules.items():
                            if rule_name == 'MODEL_PREFERENCE':
                                st.write(f"🤖 **Primary Model**: {rule_value}")
                            elif rule_name == 'FALLBACK_MODEL':
                                st.write(f"🔄 **Fallback Model**: {rule_value}")
                            elif rule_name == 'TEMPERATURE':
                                st.write(f"🌡️ **Temperature**: {rule_value}")
                            elif rule_name == 'MAX_RETRIES':
                                st.write(f"🔁 **Max Retries**: {rule_value}")
                            else:
                                st.write(f"• **{rule_name}**: {rule_value}")

def generate_copy_for_platform(prompt_template, user_input, platform_rules=None, client_data=None, legacy_advisors=False):
    """Generate copy using AI with rule-based enhancement"""
    # Replace the placeholder in the prompt
    final_prompt = prompt_template.replace("{USER_INPUT}", user_input)
    
    # Extract and apply rules if available
    if platform_rules:
        logger.log_operation_start("rule_application", platform=platform_rules.get('PLATFORM', 'unknown'))
        
        # Add rule-based constraints to the prompt
        rule_constraints = []
        
        if 'CHARACTER_LIMIT' in platform_rules:
            rule_constraints.append(f"- STRICT CHARACTER LIMIT: {platform_rules['CHARACTER_LIMIT']} characters maximum")
            
        if 'HASHTAG_COUNT' in platform_rules:
            hashtag_info = platform_rules['HASHTAG_COUNT']
            if isinstance(hashtag_info, dict):
                rule_constraints.append(f"- HASHTAGS: Use {hashtag_info['min']}-{hashtag_info['max']} hashtags")
            else:
                rule_constraints.append(f"- HASHTAGS: Use {hashtag_info} hashtags")
                
        if 'EMOJI_ALLOWED' in platform_rules and not platform_rules['EMOJI_ALLOWED']:
            rule_constraints.append("- NO EMOJIS allowed")
            
        if 'EM_DASH_ALLOWED' in platform_rules and not platform_rules['EM_DASH_ALLOWED']:
            rule_constraints.append("- NO EM-DASHES allowed")
            
        if 'REQUIRED_CTA' in platform_rules and platform_rules['REQUIRED_CTA']:
            rule_constraints.append("- MUST include a clear call-to-action")
            
        if 'TONE_STYLE' in platform_rules:
            rule_constraints.append(f"- TONE: {platform_rules['TONE_STYLE']}")
            
        if 'ENGAGEMENT_RULES' in platform_rules:
            rule_constraints.append(f"- FORBIDDEN: {platform_rules['ENGAGEMENT_RULES']}")
        
        if rule_constraints:
            constraints_text = "\n".join(rule_constraints)
            final_prompt = f"""PLATFORM RULES (MUST BE FOLLOWED EXACTLY):
{constraints_text}

{final_prompt}

REMINDER: Follow all platform rules above exactly. Character limits are strict."""
    
    # Add client context if available
    if client_data:
        client_context = f"""
CLIENT CONTEXT:
- Client: {client_data.get('name', 'Unknown')}
- Brand Voice: {client_data.get('brand_voice', 'Professional')}
- Tone: {client_data.get('tone', 'Neutral')}
- Industry: {client_data.get('industry', 'General')}

IMPORTANT: Follow the client's brand voice and tone exactly.

"""
        final_prompt = client_context + final_prompt
    
    # Add Legacy Advisors prompt if checkbox is selected
    if legacy_advisors:
        final_prompt = final_prompt + "\n\n" + LEGACY_ADDON_PROMPT
    
    try:
        # Use centralized configuration with platform rule overrides
        model_preference = platform_rules.get('MODEL_PREFERENCE') if platform_rules else None
        if not model_preference:
            model_preference = tool_config.get('MODEL_PREFERENCE', 'gemini-1.5-flash')
        
        temperature = platform_rules.get('TEMPERATURE') if platform_rules else None
        if temperature is None:
            temperature = tool_config.get('TEMPERATURE', 0.7)
            
        fallback_model = platform_rules.get('FALLBACK_MODEL') if platform_rules else None
        if not fallback_model:
            fallback_model = tool_config.get('FALLBACK_MODEL', 'gpt-4')
        
        logger.info("Generating copy with rules", 
                   model=model_preference, temperature=temperature, 
                   rules_applied=len(platform_rules) if platform_rules else 0)
        
        # Try primary model first (using universal framework functions with rules)
        if 'gemini' in model_preference.lower():
            response = call_gemini_api(final_prompt, temperature=temperature, context_rules=platform_rules)
            if not response.startswith('Error:'):
                return response
        
        # Fallback to secondary model
        response = call_openai_api(final_prompt, model=fallback_model, temperature=temperature, context_rules=platform_rules)
        return response
            
    except Exception as e:
        logger.error("Copy generation failed", error=str(e))
        return f"Error: {str(e)}"

def run():
    """Main function called by app.py """ 
    # Retro game style header
    st.markdown("""
        <div style="text-align: center; padding: 20px; background: #000; border: 3px solid #0ff; margin-bottom: 30px;">
            <h1 style="font-family: 'Courier New', monospace; color: #0ff; font-size: 48px; 
                       text-shadow: 2px 2px #f0f; margin: 0; letter-spacing: 8px;">
                COPY GENERATOR
            </h1>
            <p style="font-family: 'Courier New', monospace; color: #0f0; font-size: 20px; margin-top: 10px;">
                [ LEVEL 1 - INSERT CONTENT TO BEGIN ]
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Show selected client info
    selected_client = st.session_state.get("selected_client")
    if selected_client:
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: #1a1a1a; border: 2px solid #0f0; margin-bottom: 20px;">
                <p style="font-family: 'Courier New', monospace; color: #0f0; font-size: 22px; margin: 0;">
                    PLAYER: {selected_client['name'].upper()}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Track uploaded filename for download naming
    if "uploaded_filename" not in st.session_state:
        st.session_state["uploaded_filename"] = None
    
    # Center the input section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Retro styled input container
        st.markdown("""
            <div style="background: #1a1a1a; padding: 30px; border: 2px solid #f0f; 
                        box-shadow: 0 0 20px rgba(255,0,255,0.5); margin-bottom: 20px;">
                <p style="font-family: 'Courier New', monospace; color: #f0f; font-size: 24px; 
                          text-align: center; margin-bottom: 20px;">
                    ⟨ INPUT TERMINAL ⟩
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # File uploader with custom label
        st.markdown("""
            <p style="font-family: 'Courier New', monospace; color: #ff0; font-size: 18px;">
                ▶ LOAD FILE [OPTIONAL]
            </p>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=None, label_visibility="collapsed")
        
        # Notes input with custom label
        st.markdown("""
            <p style="font-family: 'Courier New', monospace; color: #ff0; font-size: 18px; margin-top: 20px;">
                ▶ ENTER NOTES [OPTIONAL]
            </p>
        """, unsafe_allow_html=True)
        notes = st.text_area("", height=150, label_visibility="collapsed", 
                            placeholder="Type your content here...")
        
        # Checkboxes and button section
        st.markdown("""
            <div style="background: #2a2a2a; padding: 20px; margin-top: 20px; border: 1px solid #0ff;">
        """, unsafe_allow_html=True)
        
        # Legacy Advisors checkbox with custom styling
        legacy_advisors = st.checkbox("⚡ LEGACY ADVISORS MODE", key="legacy_advisors_checkbox")
        
        # Generate button - centered
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            generate_clicked = st.button("🎮 GENERATE COPY", key="generate_copy_button", 
                                        use_container_width=True,
                                        type="primary")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Generate copy when button is clicked
    if generate_clicked:
        # Combine file content and notes
        user_input = ""
        
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")
            user_input += file_content
            # Store the filename without extension
            st.session_state["uploaded_filename"] = os.path.splitext(uploaded_file.name)[0]
            
        if notes.strip():
            if user_input:
                user_input += "\n\n"
            user_input += notes
        
        if user_input.strip():
            # Load prompts and rules
            prompts, prompt_rules = load_all_prompts()
            
            if not prompts:
                st.error("No prompts found! Check your prompts/copy_prompts/social_prompts folder.")
                return
            
            # Store generated content in session state
            if "generated_outputs" not in st.session_state:
                st.session_state["generated_outputs"] = {}
            
            # Create retro gaming loading screen
            generating_placeholder = st.empty()
            generating_placeholder.markdown("""
                <div style="background: #000; padding: 60px; border: 4px solid #0ff; box-shadow: 0 0 20px #0ff; position: relative; overflow: hidden;">
                    <h1 style="font-family: 'Courier New', monospace; color: #0ff; font-size: 64px; 
                               text-align: center; margin: 0; text-shadow: 0 0 10px #0ff;
                               animation: glitch 0.3s infinite;">
                        GENERATING COPY NOW
                    </h1>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-family: 'Courier New', monospace; color: #f0f; font-size: 36px;
                                    animation: blink 0.5s infinite;">
                            ▓▓▓▓▓▓▓▓▓▓
                        </span>
                    </div>
                    <p style="font-family: 'Courier New', monospace; color: #0f0; font-size: 24px; 
                              text-align: center; animation: slide 2s infinite linear;">
                        LOADING RULE-ENHANCED COPY... PLEASE WAIT...
                    </p>
                    <div style="position: absolute; top: 20px; right: 20px; font-family: 'Courier New', monospace; 
                                color: #ff0; font-size: 20px; animation: spin 2s infinite linear;">
                        ◢◣◤◥
                    </div>
                </div>
                <style>
                    @keyframes glitch {
                        0%, 100% { text-shadow: 0 0 10px #0ff, -2px 0 #f0f, 2px 0 #0f0; }
                        25% { text-shadow: 0 0 10px #0ff, 2px 0 #f0f, -2px 0 #0f0; }
                        50% { text-shadow: 0 0 10px #0ff, -2px 2px #f0f, 2px -2px #0f0; }
                        75% { text-shadow: 0 0 10px #0ff, 2px -2px #f0f, -2px 2px #0f0; }
                    }
                    @keyframes blink {
                        0%, 49% { opacity: 1; }
                        50%, 100% { opacity: 0; }
                    }
                    @keyframes slide {
                        0% { transform: translateX(-100%); }
                        100% { transform: translateX(100%); }
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            """, unsafe_allow_html=True)
            
            with st.spinner("Generating rule-enhanced copy for all platforms..."):
                # Generate for each platform with rules
                for platform_name, prompt_template in prompts.items():
                    platform_rule_set = prompt_rules.get(platform_name, {})
                    generated_copy = generate_copy_for_platform(
                        prompt_template, 
                        user_input, 
                        platform_rule_set,
                        selected_client,
                        legacy_advisors
                    )
                    st.session_state["generated_outputs"][platform_name] = generated_copy
            
            # Clear the loading screen
            generating_placeholder.empty()
            
            # Display rule summary
            display_rule_summary(prompt_rules)
            
            # Easter egg: Self-deprecating success messages
            import random
            success_messages = [
                "✅ Holy fuck, it actually worked!",
                "😱 Wait, what? It didn't crash? That's new...",
                "🤯 Copy generated! Jon's shocked too!",
                "💀 Somehow this janky code produced copy!",
                "🎲 You rolled a nat 20! Copy generated despite Jon's code!",
                "🔥 It's on fire! Oh wait, that's just your hot copy!",
                "⚠️ Warning: Copy generated successfully (we're as surprised as you)",
                "🎯 Task failed successfully! Wait no, it actually worked!",
                "🤔 Copy generated... Jon still doesn't know how",
                "💩 Holy shit! The copy generator didn't shit the bed!",
                "🙏 Miracle detected: Copy generated without explosions!",
                "🎰 Jackpot! All systems somehow didn't fail!",
                "🚨 ALERT: Something went right for once!",
                "🎪 The circus of code somehow produced copy!",
                "☠️ Copy generated! The code gods have mercy today!"
            ]
            st.success(random.choice(success_messages))
            st.rerun()  # Refresh to show results
        else:
            # Easter egg: Self-deprecating error messages
            import random
            error_messages = [
                "🤦 Please upload a file or enter some notes, you beautiful disaster!",
                "❌ No input? Even Jon's code needs SOMETHING to work with!",
                "💔 You broke it already? Just kidding, you need to add content first!",
                "🙈 Error: User smarter than code. Please provide input!",
                "🎭 Plot twist: You need to actually give it something to copy!",
                "🤡 Nice try! But this circus needs some content to perform!",
                "📝 Feed me content, Seymour! (File or notes required)",
                "🍕 No input? That's like pizza without cheese - just wrong!",
                "🚫 404: Content not found. Jon's fault? Probably. Your fault? Definitely!",
                "💀 RIP: Died from lack of input. Please resuscitate with content!"
            ]
            st.error(random.choice(error_messages))
    
    # Show generated outputs if they exist
    if "generated_outputs" in st.session_state and st.session_state["generated_outputs"]:
        # Retro game style output header
        st.markdown("""
            <div style="text-align: center; padding: 15px; background: #000; 
                        border: 3px solid #0f0; margin: 30px 0 20px 0;">
                <h2 style="font-family: 'Courier New', monospace; color: #0f0; font-size: 32px; 
                           margin: 0; animation: pulse 2s infinite;">
                    ⚡ OUTPUT TERMINAL ⚡
                </h2>
                <p style="font-family: 'Courier New', monospace; color: #ff0; font-size: 18px; margin-top: 10px;">
                    [ COPY GENERATION COMPLETE - LEVEL CLEARED! ]
                </p>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Center the outputs
        col1_out, col2_out, col3_out = st.columns([0.5, 3, 0.5])
        with col2_out:
            # Show outputs in a retro styled grid
            outputs = st.session_state["generated_outputs"]
            
            for platform_name, content in outputs.items():
                # Platform header with retro styling
                st.markdown(f"""
                    <div style="background: #1a1a1a; border: 2px solid #0ff; padding: 10px; 
                                margin-bottom: 10px;">
                        <p style="font-family: 'Courier New', monospace; color: #0ff; 
                                  font-size: 20px; margin: 0; text-align: center;">
                            ▸ {platform_name.upper()} ◂
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.text_area(
                    "",
                    value=content,
                    height=150,
                    key=f"output_{platform_name}_{id(content)}",
                    label_visibility="collapsed"
                )
        
        # Action buttons section with retro styling
        st.markdown("""
            <div style="text-align: center; padding: 20px; background: #1a1a1a; 
                        border: 3px solid #ff0; margin-top: 20px;">
                <p style="font-family: 'Courier New', monospace; color: #ff0; font-size: 22px; margin-bottom: 15px;">
                    ⟨ GAME CONTROLS ⟩
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1, 2, 0.5, 2, 1])
        with col2:
            file_bytes = outputs_to_txt_bytes(outputs)
            from datetime import datetime
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Use uploaded filename if available, otherwise default to copy_generator
            prefix = st.session_state.get("uploaded_filename", "copy_generator")
            if not prefix:
                prefix = "copy_generator"
            file_name = f"{prefix}_{now}.txt"
            
            st.download_button(
                label="💾 SAVE GAME",
                data=file_bytes,
                file_name=file_name,
                mime="text/plain",
                key="download_results",
                use_container_width=True
            )
        
        # Clear results button
        with col4:
            if st.button("🗑️ GAME OVER", key="clear_results", use_container_width=True):
                del st.session_state["generated_outputs"]
                st.session_state["uploaded_filename"] = None
                
                # Easter egg: Random clear messages
                import random
                clear_messages = [
                    "💥 Results deleted. They're fucking gone.",
                    "🔥 Burned to the ground.",
                    "🗑️ Thrown in the trash where they belong.",
                    "💀 Dead. Buried. Forgotten.",
                    "🚮 Yeeted into the void.",
                    "✨ Vanished. Like my will to code properly.",
                    "👻 Ghosted.",
                    "🌪️ Wiped clean. Start over, you masochist."
                ]
                st.info(random.choice(clear_messages))
                import time
                time.sleep(0.8)
                st.rerun()