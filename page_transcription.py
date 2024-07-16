import streamlit as st
import streamlit as st
from openai import OpenAI
import utils

def transcribe_audio():
    """Transcribes the uploaded audio file using OpenAI's API."""
    if 'user_api_key' not in st.session_state or 'audio_file' not in st.session_state:
        st.error("API-Schlüssel oder Audiodatei nicht im Sitzungszustand gefunden.")
        return
    
    client = OpenAI(api_key=st.session_state.user_api_key)
    
    try:
        with st.spinner('Transkribieren... Bitte warten.'):
            audio_file = st.session_state.audio_file
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text"
            )
            st.success('Transkription abgeschlossen!')
            transcription = transcription.replace("ß", "ss")
            return transcription  # Directly return the plain text transcription
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
        return None

def extract_text_from_text_box(text):
    """Extracts text from the text box and prepares it for further processing."""
    character_count = len(text)
    text_and_pages = {"pages": []}
    text_and_pages["pages"].append({
        "page_number": 1,
        "page_text": text
    })    
    return text_and_pages, character_count

def display_page_transcription():
    """Displays the transcription page."""
    utils.print_heading("Transkribierung", "Schliesse das Browserfenster nicht.")

    if st.session_state.raw_text is None:
        st.session_state.raw_text = transcribe_audio()  # Transcribe the audio

    if st.session_state.raw_text is not None:
        st.session_state.raw_text = st.text_area(
            "Du kannst den transkribierten Text gegebenenfalls noch anpassen.",
            value=st.session_state.raw_text,
            height=300
        )
        st.session_state.text_input_valid = True
        st.session_state.processing_text, st.session_state.character_count = extract_text_from_text_box(st.session_state.raw_text)

    utils.page_navigation_button_grid("Zurück zum Hauptmenü", "Weiter", "page_start", "page_configuration", col_widths=[7.8, 0.1, 1.1], reset_session_state_on_back_activation = True)
