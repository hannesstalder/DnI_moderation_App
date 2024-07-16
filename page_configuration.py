import streamlit as st
import math
import utils

def estimate_metrics(character_count, chunk_size):
    """Estimates the price and time for processing."""
    input_token_price = 5 / 1e6
    output_token_price = 15 / 1e6

    base_input_characters = 1100
    base_output_characters = 300

    estimated_time_per_chunk = 4.5

    chunk_count = math.ceil(character_count / chunk_size)

    estimated_time = chunk_count * estimated_time_per_chunk

    estimated_price = ((chunk_count * base_input_characters + character_count) * 0.25) * input_token_price + (chunk_count * base_output_characters * 0.25) * output_token_price

    return estimated_price, estimated_time

def display_metrics(character_count, chunk_size):
    """Displays the estimated price and time for processing."""
    estimated_price_franken, estimated_duration_seconds = estimate_metrics(character_count, chunk_size)
    
    estimated_price_rappen = estimated_price_franken * 100

    minutes = estimated_duration_seconds // 60
    seconds = estimated_duration_seconds % 60

    col1, col2, col3 = st.columns([0.25, 0.1, 1])

    with col1:
        st.metric(label="Geschätzter Preis", value=f"{estimated_price_rappen:.2f} Rp.")

    with col3:
        st.metric(label="Geschätzte Verarbeitungsdauer", value=f"{int(minutes)} Min {int(seconds)} Sek")

def display_page_configuration():
    """Displays the configuration page."""
    st.title("Konfiguration")

    display_metrics(st.session_state.character_count, st.session_state.chunk_size)
    if st.session_state.current_main_path == "text":
        utils.page_navigation_button_grid("Zurück", "Datenverarbeitung starten", "page_text_processing", "page_run", col_widths=[0.25, 0.1, 1])
    if st.session_state.current_main_path == "audio":
        utils.page_navigation_button_grid("Zurück", "Datenverarbeitung starten", "page_transcription", "page_run", col_widths=[0.25, 0.1, 1])