# frameworks/copy_generator_framework.py
import streamlit as st

def run_copy_generator(
    tool_name="Copy Generator",
    sidebar_info=None,
    left_text_label="Notes",
    right_box_labels=None,
    box_values=None,
    generate_func=None,  # New: function to generate copy
    prompts_dict=None,   # New: dictionary of platform prompts
):
    if right_box_labels is None:
        right_box_labels = ["Facebook", "LinkedIn", "Bluesky", "TikTok", "Generic"]
    if box_values is None:
        box_values = [""] * len(right_box_labels)

    if sidebar_info:
        sidebar_info()

    st.header(tool_name)

    # Get selected client from session state
    selected_client = st.session_state.get("selected_client")
    
    # Show client info if selected
    if selected_client:
        st.success(f"🎯 Generating for: **{selected_client['name']}**")
        with st.expander("Client Context"):
            st.write(f"**Brand Voice:** {selected_client['brand_voice']}")
            st.write(f"**Tone:** {selected_client['tone']}")
            st.write(f"**Industry:** {selected_client['industry']}")

    # Layout: 2 columns, left (1), right (3)
    col_left, col_right = st.columns([.8, 4])

    with col_left:
        uploaded_file = st.file_uploader("Drag & Drop a file here", type=None, label_visibility="visible")
        notes = st.text_area(left_text_label, height=140)
        
        # Generate button
        if st.button("🚀 Generate Copy", key="generate_copy_btn"):
            if notes.strip() and generate_func and prompts_dict:
                # Generate copy for each platform
                generated_outputs = {}
                for label in right_box_labels:
                    if label.lower() in prompts_dict:
                        platform_copy = generate_func(
                            platform=label.lower(),
                            user_input=notes,
                            client_data=selected_client,
                            prompt_template=prompts_dict[label.lower()]
                        )
                        generated_outputs[label] = platform_copy
                        # Update the UI
                        st.session_state[f"copy_gen_{label}"] = platform_copy
                
                st.success("✅ Copy generated for all platforms!")

    with col_right:
        # Display text areas for each platform
        for label, value in zip(right_box_labels, box_values):
            # Get generated value from session state if exists
            display_value = st.session_state.get(f"copy_gen_{label}", value)
            st.text_area(label, value=display_value, height=70, key=f"copy_gen_{label}")

    return uploaded_file, notes