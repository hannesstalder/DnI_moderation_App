import streamlit as st
import streamlit as st
import functions_extract_text_from_file
import functions_extract_text_from_url
from urllib.parse import urlparse
import utils

def input_option_select(max_chars):
    input_options = ["Text eingeben oder hineinkopieren", "PDF-Datei hochladen", "Word-Datei hochladen", "Text von einer Website prüfen"]                     
    selected_option = st.selectbox('Wähle die gewünschte Funktion aus:', input_options)

    if selected_option == "Text eingeben oder hineinkopieren":
        form_text_box(max_chars)
    elif selected_option == "PDF-Datei hochladen":
        form_pdf(max_chars)
    elif selected_option == "Word-Datei hochladen":
        form_word(max_chars)
    elif selected_option == "Text von einer Website prüfen":
        form_url(max_chars)

def form_text_box(max_chars):
    text_input = st.text_area("Kopiere deinen Text in die Textbox und drücke danach CTRL + Enter", height=300)
    character_count = len(text_input)

    if character_count > max_chars:
        st.error(f"Dein Text überschreitet mit {character_count} Zeichen das Maximum von {max_chars}. Bitte gib einen kürzeren Text ein.")
        st.session_state.text_input_valid = False
    elif character_count == 0:
        st.session_state.text_input_valid = False
    else:
        st.session_state.processing_text, st.session_state.character_count = functions_extract_text_from_file.extract_text_from_text_box(text_input)
        st.session_state.text_input_valid = True

def form_pdf(max_chars):
    pdf_file = st.file_uploader("Lade eine PDF-Datei hoch.", type=['pdf'])
    if pdf_file is not None:
        processing_text, character_count = functions_extract_text_from_file.extract_text_from_pdf(pdf_file, functions_extract_text_from_file.clean_text_smart)
        if character_count > max_chars:
            st.error(f"Der Text in deinem PDF überschreitet mit {character_count} Zeichen das Maximum von {max_chars}. Bitte lade ein PDF mit weniger Text hoch.")
            st.session_state.text_input_valid = False
        else:
            st.session_state.processing_text, st.session_state.character_count = processing_text, character_count
            st.session_state.text_input_valid = True

def form_word(max_chars):
    word_file = st.file_uploader("Lade eine Word-Datei hoch.", type=['docx'])
    if word_file is not None:
        processing_text, character_count = functions_extract_text_from_file.extract_text_from_word(word_file, functions_extract_text_from_file.clean_text_smart)
        if character_count > max_chars:
            st.error(f"Der Text in deinem Word-Dokument überschreitet mit {character_count} Zeichen das Maximum von {max_chars}. Bitte lade ein Word-Dokument mit weniger Text hoch.")
            st.session_state.text_input_valid = False
        else:
            st.session_state.processing_text, st.session_state.character_count = processing_text, character_count
            st.session_state.text_input_valid = True

def form_url(max_chars):
    page_url = st.text_input("Gib die URL der Website ein, deren Text du prüfen willst.")
    
    if st.button("URL bestätigen"):
        st.session_state.url_confirmed = True
    
    if st.session_state.url_confirmed:
        try:
            # Validate URL format
            parsed_url = urlparse(page_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                st.error("Die eingegebene URL ist ungültig. Bitte gib eine gültige URL ein.")
                st.session_state.url_confirmed = False
                return False

            page_html = functions_extract_text_from_url.fetch_html(page_url)
            if not page_html:
                st.error("Fehler: Die URL konnte nicht abgerufen werden. Bitte überprüfe die URL und versuche es erneut.")
                st.session_state.url_confirmed = False
                return False
            st.success("URL gültig.")

            page_text = functions_extract_text_from_url.extract_text_from_html_selective(page_html)
            character_count = len(page_text)

            if character_count > max_chars:
                st.error(f"Der Text auf der Website überschreitet mit {character_count} Zeichen das Maximum von {max_chars}. Bitte gib die URL einer Website mit weniger Text ein.")
                st.session_state.text_input_valid = False
                return False
            else:
                st.session_state.processing_text, st.session_state.character_count = functions_extract_text_from_file.extract_text_from_text_box(page_text)
                st.session_state.text_input_valid = True
                return True
            
        except Exception as e:
            st.error(f"Bitte überprüfe die URL und versuche es erneut. Fehler: {e}.")
            st.session_state.url_confirmed = False
            return False

def display_page_text_processing():
    """Displays the text processing page."""
    utils.print_heading("Textverarbeitung", "Hier kannst du Text direkt in ein Textfeld kopieren, Dateien wie PDF- oder Worddateien hochladen oder auch eine URL eingeben, um den Text auf einer Webseite zu prüfen.")

    max_chars = 500000
    input_option_select(max_chars)

    utils.page_navigation_button_grid("zurück zum Hauptmenü",
                                      "Weiter",
                                      "page_start",
                                      "page_configuration",
                                      col_widths=[7.8, 0.1, 1.1],
                                      return_visible_condition=True,
                                      continue_visible_condition=st.session_state.text_input_valid,
                                      reset_session_state_on_back_activation=True)
