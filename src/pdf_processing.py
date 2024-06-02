import fitz
import re
from typing import Dict, List
from entity_extraction import extract_ordinary_entities
from exceptions import CorruptedPDFFile, UnableToOpenPDFFile
import subprocess


def is_real_pdf(path):
    """
    Check if a file is a real PDF using the 'file' command. Unfortunately, Flask check only content-type
    which is not always accurate.

    Parameters:
    path (str): Path to the file.

    Returns:
    bool: True if the file is a real PDF, False otherwise.

    Raises:
    subprocess.CalledProcessError: If the 'file' command fails.
    ValueError: If the output does not contain 'application/pdf'.
    """
    try:
        result = subprocess.run(['file', '--mime-type', path], capture_output=True, text=True, check=True)
        if "application/pdf" in result.stdout:
            return True
        else:
            raise CorruptedPDFFile("Not a PDF file")
    except subprocess.CalledProcessError as e:
        raise e


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file.

    Parameters:
    pdf_path (str): Path to the PDF file.

    Returns:
    str: Extracted text from the PDF.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise UnableToOpenPDFFile(f"An error occurred while opening the PDF file: {e}")

    text = ""
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            text += page.get_text()
        except Exception as e:
            print(f"An error occurred while processing page {page_num}: {e}")

    doc.close()
    return text


def filter_entities(entities: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Filters and categorizes entities from a dictionary of entities.

    Parameters:
    entities (Dict[str, str]): A dictionary with entity names as keys and their types as values.

    Returns:
    Dict[str, List[str]]: A dictionary with entity types as keys and lists of entity names as values.
    """
    # Initialize dictionary to store extracted entities by type
    extracted_entities = {'PERSON': [], 'NORP': [], 'GPE': [], 'CARDINAL': []}

    # Iterate through the dictionary and extract required entities
    for key, value in entities.items():
        if value in extracted_entities:
            extracted_entities[value].append(key)

    return extracted_entities


def clean_text(text: str) -> str:
    """
    Cleans the input text by removing URLs, names, countries, email addresses, special characters, and punctuation.

    Parameters:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text in lowercase.
    """
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip().replace('\n', ' ')

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove special characters
    text = re.sub(r'[^A-Za-z0-9\s]+', '', text)

    # Extract entities to remove
    ordinary_entities = extract_ordinary_entities(text)
    entities_to_remove = filter_entities(ordinary_entities)

    # Remove entities from text
    for entity_list in entities_to_remove.values():
        for entity in entity_list:
            text = text.replace(entity, '')

    return text.lower()
