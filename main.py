import streamlit as st
import streamlit as st
import page_start
import page_text_processing
import page_audio_processing
import page_transcription
import page_configuration
import page_run
import page_results

def main():
    initialize_session_state()

    views = {
        "page_start": page_start.display_page_start,
        "page_text_processing": page_text_processing.display_page_text_processing,
        "page_audio_processing": page_audio_processing.display_page_audio_processing,
        "page_transcription": page_transcription.display_page_transcription,
        "page_configuration": page_configuration.display_page_configuration,
        "page_run": page_run.display_page_run,
        "page_results": page_results.display_page_results,
    }

    view_function = views.get(st.session_state.current_view, page_start.display_page_start)
    view_function()

def initialize_session_state():
    defaults = {
        "current_view": "page_start",
        "current_main_path": None,
        "processing_text": None,
        "raw_text": None,
        "text_input_valid": False,
        "character_count": 0,
        "url_confirmed": False,
        "audio_file": None,
        "audio_file_valid": False,
        "user_assistant_id": "",
        "user_api_key": "",
        "authorized": False,
        "chunk_size": 1,
        "prepared_data": None,
        "processed_data": None,
        "api_processing_complete": False,
        "api_processing_running": False,
        "show_results": False,
        "text_imperfect": False,
        "chunk_size": 300
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

main()