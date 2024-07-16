import streamlit as st

def reset_session_state():
    """Resets the session state to its initial values."""
    keys_to_reset = [
        "current_view", "current_main_path", "previous_view", "processing_text", "raw_text", "text_input_valid",
        "character_count", "url_confirmed", "audio_file", "audio_file_valid", "authorized", "chunk_size",
        "prepared_data", "processed_data", "api_processing_complete",
        "api_processing_running", "show_results", "text_imperfect"
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)
    st.session_state.current_view = "page_start"
    st.session_state.previous_view = "page_start"

def return_to_start():
    """Handles the return to start button click event."""
    if st.button("zurück zum Hauptmenü"):
        reset_session_state()
        st.rerun()

def continue_to_next_page(button_text, current_view, next_view):
    """Handles the continue button click event."""
    if st.button(button_text):
        st.session_state.previous_view = current_view
        st.session_state.current_view = next_view
        st.rerun()

def navigation_button_grid(return_button_text, continue_button_text, current_view, next_view, col_widths=[7.8, 0.1, 1.1]):
    """Displays the navigation buttons with customizable spacing."""
    col1, col2, col3 = st.columns(col_widths)  # Using customizable spacing
    with col1:
        return_to_start()
    with col3:
        if st.session_state.text_input_valid and st.session_state.authorized:
            continue_to_next_page(continue_button_text, current_view, next_view)

def print_heading(title, subtitle):
    """Prints the heading for the current page."""
    st.title(title)
    st.markdown(subtitle)

def page_navigation_button_grid(
    return_button_text, 
    continue_button_text, 
    previous_page, 
    next_page, 
    col_widths=[7.8, 0.1, 1.1], 
    return_visible_condition=True, 
    continue_visible_condition=True,
    reset_session_state_on_back_activation=False
):
    """Displays the navigation buttons with customizable spacing and conditions."""
    col1, col2, col3 = st.columns(col_widths)  # Using customizable spacing
    with col1:
        if return_visible_condition:
            change_current_view(return_button_text, previous_page, reset_session_state_on_back_activation)
    with col3:
        if continue_visible_condition:
            change_current_view(continue_button_text, next_page, False)

def change_current_view(button_text, page, reset_session_state_on_back_activation):
    """Handles the button click event."""
    if st.button(button_text):
        if reset_session_state_on_back_activation == True:
            reset_session_state()
        st.session_state.current_view = page
        st.rerun()

def debug_display_session_states():
    """Displays all session states for debugging."""
    session_states = [
        "current_view", "current_main_path", "previous_view", "processing_text", "raw_text", "text_input_valid",
        "character_count", "url_confirmed", "audio_file", "audio_file_valid", "user_assistant_id", "user_api_key",
        "authorized", "chunk_size", "prepared_data", "processed_data", "api_processing_complete",
        "api_processing_running", "show_results", "text_imperfect"
    ]
    
    debug_info = []
    for key in session_states:
        value = st.session_state.get(key, "Not Set")
        debug_info.append(f"<b>{key}:</b> {value}")
    
    st.markdown("<br>".join(debug_info), unsafe_allow_html=True)
