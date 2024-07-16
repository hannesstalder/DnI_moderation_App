import streamlit as st
from mutagen import File
import math
import io
import utils
def upload_audio_file(max_size_bytes=25 * 1_000_000):
    """Handles the upload of an audio file and validates its size."""
    audio_file = st.file_uploader("Upload an audio file.", type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'])
    if audio_file:
        if audio_file.size > max_size_bytes:
            st.error("Die Datei überschreitet die maximal zugelassene Grösse von 25 MB.")
        else:
            st.session_state.audio_file_valid = True
            return audio_file
    return None

def get_audio_length(file):
    """Returns the length of the audio file in seconds."""
    try:
        file_buffer = io.BytesIO(file.read())
        audio = File(file_buffer)
        if audio.info and hasattr(audio.info, 'length'):
            return audio.info.length
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Audiodatei: {e}")
    return None

def calculate_transcription_price(audio_file):
    """Calculates the price for transcribing the audio file."""
    length_seconds = get_audio_length(audio_file)
    if length_seconds:
        whisper_price_per_minute = 0.006 * 0.9 * 100  # Dollar to Rappen
        minutes = math.ceil(length_seconds / 60)  # rounding up the number of minutes
        return round(minutes * whisper_price_per_minute, 2)  # Round to nearest cent
    return 0

def display_page_audio_processing():
    """Displays the audio processing page."""
    utils.print_heading(
        "Audioverarbeitung",
        "Hier kannst du Dateien mit Audio hochladen. Danach wird ein Transkript aus dem Audio erstellt, "
        "welches anschliessend als Text weiterverarbeitet wird.\nAchtung, das Bildmaterial einer mp4-Datei wird nicht beachtet."
    )
    audio_file = upload_audio_file()
    if audio_file:
        st.session_state.audio_file = audio_file
        st.audio(st.session_state.audio_file)
        price = calculate_transcription_price(audio_file)
        st.success(f"Die Transkribierung wird ca. {price} Rappen kosten.")
    utils.page_navigation_button_grid("Zurück",
                                      "Kostenpflichtig transkribieren",
                                      "page_start", "page_transcription",
                                      col_widths=[1, 0.72, 0.88],
                                      return_visible_condition=True,
                                      continue_visible_condition=(st.session_state.audio_file_valid and st.session_state.authorized),
                                      reset_session_state_on_back_activation=True)

