from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .constants import ALLOWED_FILE_TYPES
from .models import CorpusFile
from datetime import datetime, timedelta
from nltk.stem import PorterStemmer
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader
from pymongo import MongoClient
import pytesseract
import filetype
import hashlib
import shutil
import csv
import os
import re

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

stemmer = PorterStemmer()

client = MongoClient('localhost', 27017)
db = client['SearchLite']  # Replace 'your_database_name' with your actual database name
postings_collection = db['Postings']  # Collection to store postings


def homepage(request):
    return render(request, 'index.html')

def process_documents(file_hashes):
    print("Running Background tasks")
    for file_hash in file_hashes:
        # Retrieve the file path from the database using file_hash
        corpus_file = CorpusFile.objects.get(file_hash=file_hash)
        file_path = os.path.join(settings.BASE_DIR, 'corpus', corpus_file.stored_file_name)
        # Extract text from the file
        text = extract_text(file_path)
        # Preprocess the text
        cleaned_text = clean_and_stem(text)
        # Update the postings
        update_postings(str(corpus_file.id), cleaned_text)
        # Update the CorpusFile object to mark processing as completed
        #corpus_file.processed = True
        #corpus_file.save()

def upload(request):
    valid_files = []
    invalid_files = []
    file_hashes = []

    if request.method == 'POST' and request.FILES.getlist('file'):
        files = request.FILES.getlist('file')
        for file in files:
            file_info = filetype.guess(file.read())
            if file_info is not None and file_info.mime in ALLOWED_FILE_TYPES:
                file_hash = generate_file_hash(file)
                if not CorpusFile.objects.filter(file_hash=file_hash).exists():
                    # Split the file name at the last occurrence of '.'
                    parts = file.name.rsplit('.', 1)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    stored_file_name = f"{parts[0]}_{timestamp}.{parts[1]}"
                    file_path = os.path.join(settings.BASE_DIR, 'corpus', stored_file_name)
                    # Save the uploaded file directly to the corpus directory
                    with open(file_path, 'wb+') as destination:
                        shutil.copyfileobj(file, destination)
                    # Add file_hash to the list for processing
                    file_hashes.append(file_hash)
                    uploaded_file = CorpusFile(
                        uploaded_file_name=file.name,
                        stored_file_name=stored_file_name,
                        file_type=file_info.mime,
                        file_size=file.size,
                        file_hash=file_hash
                    )
                    uploaded_file.save()
                    valid_files.append(file.name)
                else:
                    invalid_files.append(f"{file.name} (duplicate file)")
            else:
                invalid_files.append(f"{file.name} (invalid file type)")

        message = ''
        if valid_files:
            message += f"Files uploaded successfully: {', '.join(valid_files)}. "
        if invalid_files:
            message += f"Invalid files: {', '.join(invalid_files)}"

        if file_hashes:
            #Task.objects.create(task_name='process_documents', task_params={'file_hashes': file_hashes}, run_at=datetime.now() + timedelta(seconds=1))
            process_documents(file_hashes)

        return render(request, 'upload.html', {'message': message})

    return render(request, 'upload.html')


def search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_input', '') 
        cleaned_and_stemmed_query = clean_and_stem(search_query)
        return render(request, 'result.html')
    return render(request, 'search.html')


def generate_file_hash(file):
    try:
        file.seek(0)  # Move the file pointer to the beginning
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        file.seek(0)
        return file_hash
    except Exception as e:
        print(f"Error generating file hash: {e}")
        return None
    
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(('.doc', '.docx')):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.csv'):
        return extract_text_from_csv(file_path)
    elif file_path.endswith(('.txt', '.text')):
        return extract_text_from_text(file_path)
    elif file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        return extract_text_from_image(file_path)
    else:
        return ''

def clean_and_stem(document):
    # Remove special characters and punctuation
    cleaned_doc = re.sub(r'[^a-zA-Z\s]', '', document)
    # Convert to lowercase
    cleaned_doc = cleaned_doc.lower()
    # Tokenize by splitting
    tokens = cleaned_doc.split()
    # Stemming
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

def update_postings(doc_id, cleaned_text):
    for position, term in enumerate(cleaned_text):
        postings = postings_collection.find_one({"term": term})
        if postings is None:
            postings = {"term": term, "positions": {doc_id: [position]}}
        else:
            positions = postings.get("positions", {})
            positions[doc_id] = positions.get(doc_id, []) + [position]
            postings["positions"] = positions
        postings_collection.replace_one({"term": term}, postings, upsert=True)


def extract_text_from_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    return text
def extract_text_from_docx(file_path):
    document = Document(file_path)
    return '\n'.join([paragraph.text for paragraph in document.paragraphs])

def extract_text_from_csv(file_path):
    text = ''
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            text += ', '.join(row) + '\n'
    return text

def extract_text_from_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def extract_text_from_image(file_path):
    return pytesseract.image_to_string(Image.open(file_path), lang='eng')
