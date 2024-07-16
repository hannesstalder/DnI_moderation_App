import streamlit as st
from PIL import Image

def print_heading():
    st.title("Bildverarbeitung")
    st.markdown("Hier kannst du entwerder bis zu 10 Bilder von deinem Computer hochladen oder eine URL eingeben, um die Bilder auf einer Webseite zu prüfen.")

def return_to_start():
    if st.button("zurück zum Hauptmenu"):
        st.session_state.current_view = "start"
        st.rerun()

def continue_to_config():
    if st.button("Weiter"):
        st.session_state.previous_view = "page_image_processing"
        st.session_state.current_view = "page_configuration"
        st.rerun()

def navigation_button_grid():
    col1, col2 = st.columns([8, 1])
    with col1:
        return_to_start()
    with col2:
        st.session_state.text_input_valid = True
        if st.session_state.text_input_valid == True:
            continue_to_config()

def upload_image_files():
    max_size_bytes = 25 * 1_000_000  # Maximum file size in bytes (25 MB)
    max_files = 10  # Maximum number of images allowed

    uploaded_files = st.file_uploader("Upload up to 10 image files.", type=['png', 'jpg', 'jpeg', 'gif'], accept_multiple_files=True)
    
    if uploaded_files:
        if len(uploaded_files) > max_files:
            st.error(f"You can upload a maximum of {max_files} files.")
            return None

        total_pixel_count = 0
        valid_files = []
        
        for file in uploaded_files:
            if file.size > max_size_bytes:
                st.error(f"The file {file.name} exceeds the maximum allowed size of 25 MB.")
            else:
                image = Image.open(file)
                width, height = image.size
                pixel_count = width * height
                total_pixel_count += pixel_count
                valid_files.append(file)
        
        if valid_files:
            st.session_state.image_files_valid = True
            st.write(f"Total pixel count for all uploaded images: {total_pixel_count}")
            return valid_files, total_pixel_count

    return None

def display_page_image_processing():
    print_heading()
    valid_files, total_pixel_count = upload_image_files()
    navigation_button_grid()