import streamlit as st
import streamlit as st
import json
import datetime
import pandas as pd
from io import BytesIO
from openpyxl.styles import Alignment
from utils import return_to_start, print_heading

def highlight_string(A, B):
    """Highlights the occurrences of string B in string A."""
    formatted_B = f'***{B}***'
    return A.replace(B, formatted_B)

def display_flagged_chunks(data, surround_with_text=True):
    """Displays flagged text chunks with potential issues."""
    st.divider()

    colors = ['#DC143C', '#FF8C00', '#3CB371', '#4169E1']
    text_imperfect = False

    for section in data['sections']:
        for chunk in section.get('textChunks', []):
            if chunk.get('flag') != '0':
                text_imperfect = True

    if text_imperfect:
        st.session_state.text_imperfect = True
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.subheader("Textstelle")
        with col2:
            st.subheader("Korrektur")
        with col3:
            st.subheader("Kommentar")
        
        for section in data['sections']:
            for chunk in section.get('textChunks', []):
                if chunk.get('flag') != '0':
                    st.divider()
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        text = chunk.get('text', 'Kein Text')
                        for i, violation in enumerate(chunk.get('violations', [])):
                            color = colors[i % len(colors)]
                            text = text.replace(violation['textstring'], f"<span style='color:{color}; font-weight:bold; font-style:italic;'>{violation['textstring']}</span>")
                        st.markdown(text, unsafe_allow_html=True)
                    
                    with col2:
                        for i, violation in enumerate(chunk.get('violations', [])):
                            if i > 0:
                                st.divider()
                            color = colors[i % len(colors)]
                            st.markdown(f"<span style='color:{color}; font-weight:bold; font-style:italic;'>{violation['suggested_correction']}</span>", unsafe_allow_html=True)
                    
                    with col3:
                        for i, violation in enumerate(chunk.get('violations', [])):
                            if i > 0:
                                st.divider()
                            color = colors[i % len(colors)]
                            st.markdown(f"{violation['comment']}", unsafe_allow_html=True)
    else:
        st.markdown("Es wurden ***keine problematischen Textteile*** gefunden.")


def save_json_to_excel_user_formatted(json_data):
    """Saves the JSON data to an Excel file with user-friendly formatting."""
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        if 'documentInfo' not in data or 'sections' not in data or 'title' not in data['documentInfo']:
            st.error("Die JSON Struktur ist unvollständig oder fehlerhaft.")
            return

        file_title = data['documentInfo']['title']
        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"{file_title.replace(' ', '_').lower()}_{formatted_time}.xlsx"

        rows = []

        for section in data['sections']:
            section_id = section.get('sectionId', 'No ID').replace("page_", "Seite ")

            for chunk in section.get('textChunks', []):
                if chunk.get('flag') != '0':
                    original_text = chunk.get('text', 'Kein Text')
                    for violation in chunk.get('violations', []):
                        violation_text = violation['textstring']
                        suggested_correction = violation['suggested_correction']
                        comment = violation['comment']
                        rows.append([
                            section_id, 
                            original_text, 
                            violation_text, 
                            suggested_correction, 
                            comment
                        ])

        df = pd.DataFrame(rows, columns=['Seite', 'Textabschnitt', 'Nicht korrekte Formulierung', 'Korrekturvorschlag', 'Kommentar'])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ergebnisse')
            worksheet = writer.sheets['Ergebnisse']
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 100
            worksheet.column_dimensions['C'].width = 50
            worksheet.column_dimensions['D'].width = 50
            worksheet.column_dimensions['E'].width = 50

            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=2, max_col=5):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True)

        processed_data = output.getvalue()
        output.close()

        if st.download_button(
            label="Ergebnisse als Excel herunterladen",
            data=processed_data,
            file_name=file_name,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ):
            st.session_state.show_results = True
            st.rerun()

    except Exception as e:
        st.error(f"Es ist ein Fehler aufgetreten: {e}")

def display_page_results():
    """Displays the results page."""
    print_heading("Ergebnisse", "Hier sind die Ergebnisse. Es werden nur die Chunks angezeigt, die potentiell problematische Stellen enthalten. Weiter unten kannst du die Ergebnisse als Excel herunterladen.")
    display_flagged_chunks(st.session_state.processed_data, surround_with_text=False)
    st.divider()
    col1, col2, col3= st.columns([1.8, 0.5, 0.9])
    with col1:
        if st.session_state.text_imperfect:
            save_json_to_excel_user_formatted(st.session_state.processed_data)
    with col3:
        return_to_start()
