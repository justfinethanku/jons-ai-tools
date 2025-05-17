import streamlit as st

def run_copy_generator(
    tool_name="Copy Generator",
    sidebar_info=None,
    left_text_label="Notes",
    right_box_labels=None,
    box_values=None,
):
    if right_box_labels is None:
        right_box_labels = ["Facebook", "LinkedIn", "Bluesky", "TikTok", "Generic"]
    if box_values is None:
        box_values = [""] * len(right_box_labels)

    if sidebar_info:
        sidebar_info()

    st.header(tool_name)

    # Layout: 2 columns, left (1), right (3)
    col_left, col_right = st.columns([.8, 4])

    with col_left:
        uploaded_file = st.file_uploader("Drag & Drop a file here", type=None, label_visibility="visible")
        notes = st.text_area(left_text_label, height=140)

    with col_right:
        for label, value in zip(right_box_labels, box_values):
            st.text_area(label, value=value, height=70, key=f"copy_gen_{label}")

    # Optionally: return the file and notes for later processing
    return uploaded_file, notes 