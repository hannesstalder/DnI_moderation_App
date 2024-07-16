import streamlit as st
import PyPDF2
import docx
import re

def extract_text_from_text_box(text):
    character_count = len(text)
    text_and_pages = {"pages": []}
    text_and_pages["pages"].append({
        "page_number": 1,
        "page_text": text
    })    
    return text_and_pages, character_count

def extract_text_from_pdf(file_like_object, text_preprocessing_function):
    text_and_pages = {"pages": []}
    character_count = 0
    try:
        # Read from the file-like object
        reader = PyPDF2.PdfReader(file_like_object)

        # Loop through each page in the PDF
        for page_num, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""  # Ensure we handle None values
            preprocessed_text = text_preprocessing_function(raw_text)
            # Append the page number and text to the output dictionary
            text_and_pages["pages"].append({
                "page_number": page_num + 1,
                "page_text": preprocessed_text
            })
            # Update the character count
            character_count += len(preprocessed_text)

    except Exception as e:
        st.error(f"Beim lesen des PDF's ist ein Fehler aufgetreten: {e}")

    return text_and_pages, character_count

def extract_text_from_word(file_like_object, text_preprocessing_function):
    text_and_pages = {"pages": []}
    character_count = 0

    try:
        # Read from the file-like object
        doc = docx.Document(file_like_object)
        
        combined_text = ""

        for para in doc.paragraphs:
            raw_text = para.text or ""  # Ensure we handle None values
            preprocessed_text = text_preprocessing_function(raw_text)
            combined_text += preprocessed_text

        # Append the combined text as a single page
        text_and_pages["pages"].append({
            "page_number": 1,
            "page_text": combined_text
        })

        # Update the character count
        character_count = len(combined_text)

    except Exception as e:
        st.error(f"Beim lesen des Word-Dokuments ist ein Fehler aufgetreten: {e}")

    return text_and_pages, character_count

def clean_text_smart(text):
    # Replace newline characters (\r\n or \n) with a space to avoid joining words incorrectly.
    text = re.sub(r'\r?\n', ' ', text)

    # Remove hyphen followed by a space (commonly found at line breaks) to correctly join words split across lines.
    text = text.replace("- ", "")

    # Remove all unwanted special characters but preserve letters, numbers, common punctuation, and spaces.
    text = re.sub(r'[^\w\s,.!?;:\'-]', '', text)

    # Normalize whitespace by converting consecutive spaces to a single space and trim leading/trailing spaces.
    text = re.sub(r'\s+', ' ', text).strip()

    return text