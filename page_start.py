import streamlit as st
import hashlib
from utils import print_heading

# Configuration
HASHED_ASSISTANT_ID = "1fc3832b0f490d78702b4294e4b840e14fa915799ad50db84ae3b7a2459c2f7c"
HASHED_API_KEY = "bfcd83fd14ac440be4c6b107c70ef1ff4aac26cd4d37a3151c676a007efdb234"

def create_section(title, description, button_name, page_name):
    """Creates a section with a title, description, and button."""
    st.markdown(f"#### {title}")
    st.markdown(f"{description}")
    if st.button(button_name):
        if page_name == "page_text_processing":
            st.session_state.current_main_path = "text"
        if page_name == "page_image_processing":
            st.session_state.current_main_path = "image"
        if page_name == "page_audio_processing":
            st.session_state.current_main_path = "audio"
        st.session_state.current_view = page_name
        st.rerun()

def check_hash(input_string, expected_hash):
    """Checks if the SHA256 hash of the input string matches the expected hash."""
    return hashlib.sha256(input_string.encode()).hexdigest() == expected_hash

def get_user_input(prompt, previous_value, check_function, success_message, error_message):
    """Gets user input and checks it against a validation function."""
    user_input = st.text_input(prompt, previous_value)
    if check_function(user_input):
        st.success(success_message)
    else:
        if user_input:  # Only show this message if something was entered
            st.error(error_message)
    return user_input

def display_api_key_ui():
    """Displays the UI for entering API and Assistant keys."""
    st.markdown("#### API- und Assistentschlüssel")
    st.session_state.user_assistant_id = get_user_input(
        "Gib die Assisant-ID ein:",
        st.session_state.user_assistant_id,
        lambda x: check_hash(x, HASHED_ASSISTANT_ID),
        "Schulverlag Assistant-ID gültig!",
        "Keine Schulverlag Assistant-ID, fahre nur fort, wenn du eine gültige ID eingegeben hast!"
    )
    st.session_state.user_api_key = get_user_input(
        "Gib den API-Key ein:",
        st.session_state.user_api_key,
        lambda x: check_hash(x, HASHED_API_KEY),
        "Schulverlag API-Key gültig!",
        "Kein Schulverlag API-Key, fahre nur fort, wenn du einen gültigen Schlüssel eingegeben hast!"
    )
    st.session_state.authorized = bool(st.session_state.user_api_key and st.session_state.user_assistant_id)

def display_page_start():
    """Displays the start page."""
    print_heading("Automatische Inhaltsmoderation", 
        "Diese einfache App erlaubt es dir deine Inhalte auf korrekte Verwendung von inkulsiver, geschlechtsneutraler und diskriminierungsfreier Sprache zu prüfen.")
    display_api_key_ui()

    if st.session_state.authorized:
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            create_section(
                "Textverarbeitung",
                "Du kannst Text eingeben, PDF- und Word-Files hochladen, sowie Text von einer Webseite prüfen.",
                "weiter zur Textverarbeitung",
                "page_text_processing"
            )
        with col2:
            create_section(
                "Bildverarbeitung",
                "Lade bis zu 10 Bilder hoch oder extrahiere Bilder von einer Website.",
                "weiter zur Bildverarbeitung",
                "page_image_processing"
            )
        with col3:
            create_section(
                "Audioverarbeitung",
                "Lade eine mp3 oder eine mp4 Datei hoch, um eine Audiospur zu prüfen.",
                "weiter zur Audioverarbeitung",
                "page_audio_processing"
            )

if __name__ == "__main__":
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "start"
    if st.session_state.current_view == "start":
        display_page_start()
