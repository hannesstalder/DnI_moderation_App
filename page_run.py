import streamlit as st
import re
from openai import OpenAI
import json
import time
import utils


def prepare_document_data_for_api_call(processing_text, chunk_size):
    """Prepares the document data for the API call by splitting text into chunks."""
    document_data = {
        "documentInfo": {"title": "Inhaltsmoderation"},
        "sections": []
    }

    try:
        for page in processing_text["pages"]:
            section = {
                "sectionId": f"page_{page['page_number']}",
                "sectionTitle": f"Page {page['page_number']}",
                "textChunks": []
            }

            sentences = re.split(r'(?<=[.!?])\s+', page["page_text"])
            chunk_text = ""
            chunk_id = 1

            for sentence in sentences:
                if len(chunk_text + sentence) > chunk_size:
                    if chunk_text:
                        section["textChunks"].append({
                            "chunkId": f"chunk_{page['page_number']}_{chunk_id}",
                            "text": chunk_text.strip(),
                            "flag": [2],
                            "violations": [],                            
                        })
                        chunk_id += 1
                        chunk_text = sentence
                else:
                    chunk_text += ' ' + sentence

            if chunk_text.strip():
                section["textChunks"].append({
                    "chunkId": f"chunk_{page['page_number']}_{chunk_id}",
                    "text": chunk_text.strip(),
                    "flag": [2],
                    "violations": [],
                })

            document_data["sections"].append(section)
        
        st.session_state.prepared_data = document_data

    except Exception as e:
        st.error(f"Es ist ein Fehler beim Aufbereiten des Inhalts aufgetreten: {e}")

def print_progress(placeholder, current_chunk, chunk_count):
    """Displays the progress of the data processing."""
    with placeholder.container():
        progress = current_chunk / chunk_count
        st.progress(progress)
        st.write(f"Anfrage {current_chunk} von {chunk_count}")

def api_call(text, timeout_limit, user_assistant_id, user_api_key, status_placeholder):
    """Performs the API call to process the text and returns the flag and violations."""
    client = OpenAI(api_key=user_api_key)
    
    try:
        chat = client.beta.threads.create(
            messages=[{"role": "user", "content": f"{text}"}]
        )
    except Exception as e:
        return 3, [{
            "textstring": "error",
            "suggested_correction": "error",
            "comment": f"Error creating chat thread: {str(e)}"
        }]

    try:
        run = client.beta.threads.runs.create(thread_id=chat.id, assistant_id=user_assistant_id)
        with status_placeholder.container():
            st.write(f"Run created: {run.id}")
    except Exception as e:
        return 3, [{
            "textstring": "error",
            "suggested_correction": "error",
            "comment": f"Error creating run: {str(e)}"
        }]

    start_time = time.time()
    try:
        while run.status != "completed" and (time.time() - start_time) < timeout_limit:
            run = client.beta.threads.runs.retrieve(thread_id=chat.id, run_id=run.id)
            time.sleep(1)
    except Exception as e:
        return 3, [{
            "textstring": "error",
            "suggested_correction": "error",
            "comment": f"Error retrieving run status: {str(e)}"
        }]

    if run.status != "completed":
        return 3, [{
            "textstring": "error",
            "suggested_correction": "error",
            "comment": "Run did not complete in the allotted time."
        }]

    with status_placeholder.container():
        st.write("Run completed!")

    try:
        message_response = client.beta.threads.messages.list(thread_id=chat.id)
        messages = message_response.data

        if not messages:
            return 3, [{
                "textstring": "error",
                "suggested_correction": "error",
                "comment": "No messages received from API"
            }]

        latest_message = messages[0]
        response_json = latest_message.content[0].text.value
        response_data = json.loads(response_json)
        flag = response_data["evaluationResult"]["flag"]
        violations = response_data["evaluationResult"]["violations"]
        return flag, violations
    except Exception as e:
        with status_placeholder.container():
            st.write(f"Error processing message or parsing JSON: {e}; Message response: {message_response}")
        return 3, [{
            "textstring": "error",
            "suggested_correction": "error",
            "comment": f"Error processing message or parsing JSON: {str(e)}"
        }]

def process_data(json_data, timeout_limit, assistant_id, user_api_key, progress_placeholder, status_placeholder):
    """Processes the document data using the API and updates the session state."""
    if "sections" not in json_data:
        st.write("No sections found in JSON data.")
        return json_data

    total_chunks = sum(len(section.get("textChunks", [])) for section in json_data["sections"])
    st.session_state.chunk_count = total_chunks
    st.session_state.current_chunk = 0

    for section in json_data["sections"]:
        for chunk in section.get("textChunks", []):
            if isinstance(chunk.get("flag"), list) and any(int(item) > 1 for item in chunk["flag"]):
                flag, violations = api_call(chunk["text"], timeout_limit, assistant_id, user_api_key, status_placeholder)
                chunk["flag"] = flag
                chunk["violations"] = violations                
                st.session_state.current_chunk += 1
                print_progress(progress_placeholder, st.session_state.current_chunk, st.session_state.chunk_count)
    
    st.session_state.processed_data = json_data

def repeated_process_data(json_data, timeout_limit, assistant_id, user_api_key, progress_placeholder, status_placeholder):
    """Repeatedly processes the document data to ensure all chunks are evaluated."""
    process_data(json_data, timeout_limit, assistant_id, user_api_key, progress_placeholder, status_placeholder)
    process_data(st.session_state.processed_data, timeout_limit, assistant_id, user_api_key, progress_placeholder, status_placeholder)
    process_data(st.session_state.processed_data, timeout_limit, assistant_id, user_api_key, progress_placeholder, status_placeholder)

def initialize_processing_state():
    """Initializes the state variables for processing."""
    st.session_state.api_processing_complete = False
    st.session_state.current_chunk = 0
    st.session_state.chunk_count = sum(len(section["textChunks"]) for section in st.session_state.prepared_data["sections"])

def display_page_run():
    """Displays the data processing page and manages the processing workflow."""
    utils.print_heading("Datenverarbeitung läuft", "Schliesse das Browserfenster nicht, bis die Verarbeitung abgeschlossen ist.")

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
       
    if not st.session_state.api_processing_complete:
        st.session_state.api_processing_running = True

        if st.session_state.current_main_path == "text":
            utils.page_navigation_button_grid("Datenverarbeitung abbrechen", "weiter zum Ergebnis", "page_start", "page_results", 
                                              col_widths=[7.8, 0.1, 1.1],return_visible_condition=True,continue_visible_condition=False,reset_session_state_on_back_activation=True)
        if st.session_state.current_main_path == "audio":
            utils.page_navigation_button_grid("Datenverarbeitung abbrechen", "weiter zum Ergebnis", "page_configuration", "page_results", 
                                              col_widths=[7.8, 0.1, 1.1],return_visible_condition=True,continue_visible_condition=False,reset_session_state_on_back_activation=False)

        prepare_document_data_for_api_call(st.session_state.processing_text, st.session_state.chunk_size)
        initialize_processing_state()
        print_progress(progress_placeholder, st.session_state.current_chunk, st.session_state.chunk_count)

        repeated_process_data(
            st.session_state.prepared_data, 
            20, 
            st.session_state.user_assistant_id, 
            st.session_state.user_api_key,
            progress_placeholder,
            status_placeholder
        )

        st.session_state.api_processing_complete = True
        st.session_state.api_processing_running = False
        st.rerun()

    if st.session_state.api_processing_complete:
        st.success("Verarbeitung abgeschlossen")
        if st.session_state.current_main_path == "text":
            utils.page_navigation_button_grid("Datenverarbeitung abbrechen", "weiter zum Ergebnis", "page_start", "page_results", 
                                              col_widths=[1, 1.5, 0.85],return_visible_condition=False,continue_visible_condition=True,reset_session_state_on_back_activation=True)
        if st.session_state.current_main_path == "audio":
            utils.page_navigation_button_grid("Datenverarbeitung abbrechen", "weiter zum Ergebnis", "page_configuration", "page_results", 
                                              col_widths=[1, 1.5, 0.85],return_visible_condition=False,continue_visible_condition=True,reset_session_state_on_back_activation=False)
    