import streamlit as st
from bs4 import BeautifulSoup
import requests

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    return response.text

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()  # Remove script and style elements
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def extract_text_from_html_selective(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, and other unwanted elements
    for unwanted in soup(["script", "style", "header", "footer", "nav", "aside"]):
        unwanted.extract()

    # List of tags that usually contain the main content
    main_content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    # Extract text from the relevant elements
    relevant_elements = soup.find_all(main_content_tags)
    text_chunks = [element.get_text(strip=True) for element in relevant_elements]
    text = '\n'.join(chunk for chunk in text_chunks if chunk)
    
    return text