from nltk.stem import PorterStemmer
from django.conf import settings
import hashlib
import fitz
import nltk
import os
import re

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

stemmer = PorterStemmer()

def clean_and_stem(document):
    """
    Clean and stem the given document.

    Args:
        document (str): The document to clean and stem.

    Returns:
        list: List of stemmed tokens.
    """
    # Remove special characters and punctuation
    cleaned_doc = re.sub(r'[^a-zA-Z\s]', '', document)
    # Convert to lowercase
    cleaned_doc = cleaned_doc.lower()
    # Tokenize by splitting
    tokens = cleaned_doc.split()
    # Stemming
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

class CustomFileType:
    """
    Class to represent a custom file type.

    Attributes:
        mime (str): The MIME type of the file.
    """
    def __init__(self, mime=None):
        self.mime = mime

def generate_file_hash(file):
    """
    Generate a SHA-256 hash for the given file.

    Args:
        file (file): The file object for which to generate the hash.

    Returns:
        str: The SHA-256 hash of the file content.
    """
    try:
        file.seek(0)  # Move the file pointer to the beginning
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        file.seek(0)
        return file_hash
    except Exception as e:
        print(f"Error generating file hash: {e}")
        return None

def highlight_text_in_pdf(pdf_path, file_name, queries, color_map={}):
    """
    Highlight text in a PDF file based on multiple queries.

    Args:
        pdf_path (str): The path to the PDF file.
        file_name (str): The name of the file.
        queries (list): List of queries to highlight.

    Returns:
        str: The path to the highlighted PDF file.
    """
    pdf_document = fitz.open(pdf_path)
    output_pdf = fitz.open()

    colors = [color.lower() for color in ["YELLOW", "SKYBLUE", "ORANGE", "LIGHTBLUE",
              "ROSYBROWN", "LIGHTGREEN", "YELLOWGREEN", "LIGHTPINK",
              "LIGHTSALMON", "DARKGOLDENROD"]]

    if color_map:
        query_colors = color_map
    else:
        query_colors = {query: colors[i % len(colors)] for i, query in enumerate(queries)}
    
    query_counts = {query: 0 for query in queries}

    # Regular expression to remove escape characters
    escape_chars = re.compile(r'[\n\t\r]')

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = escape_chars.sub('', page.get_text())  # Remove escape characters from text
        for query in queries:
            if query.lower() in text.lower():
                for instance in page.search_for(query):
                    highlight = page.add_highlight_annot(instance)
                    highlight.set_colors(stroke=fitz.pdfcolor[query_colors[query]])  # use preassigned color for each query
                    highlight.update()  # update annotation
                    query_counts[query] += 1

            stemmed_query = ''.join(clean_and_stem(query))
            if stemmed_query.lower() in text.lower():
                for instance in page.search_for(stemmed_query):
                    highlight = page.add_highlight_annot(instance)
                    highlight.set_colors(stroke=fitz.pdfcolor[query_colors[query]])  # use preassigned color for each query
                    highlight.update()  # update annotation
                    query_counts[query] += 1

        output_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)

    highlighted_pdf_path = os.path.join(settings.BASE_DIR, 'highlighted_pdfs', f'{file_name}_highlighted.pdf')
    output_pdf.save(highlighted_pdf_path)
    output_pdf.close()
    pdf_document.close()

    return highlighted_pdf_path, query_counts, query_colors

