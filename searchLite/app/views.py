from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .constants import ALLOWED_FILE_TYPES
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from .models import CorpusFile
from datetime import datetime
from .text_extractor import *
from .mongo_services import *
from docx import Document
from .utils import *
import filetype
import shutil
import os

def homepage(request):
    return render(request, 'index.html')


def upload(request):
    valid_files = []
    invalid_files = []
    file_hashes = []

    if request.method == 'POST' and request.FILES.getlist('file'):
        files = request.FILES.getlist('file')
        for file in files:
            file_info = filetype.guess(file.read())
            if not file_info:
                file_info = CustomFileType()
                if file.content_type:
                    file_info.mime = file.content_type

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
            process_documents(file_hashes)

        return render(request, 'upload.html', {'message': message})

    return render(request, 'upload.html')



def search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_input', '') 
        cleaned_and_stemmed_query = clean_and_stem(search_query)
        
        # Find documents matching the exact sequence of query terms
        result = {}
        try:
            if len(cleaned_and_stemmed_query) == 1:
                single_term = cleaned_and_stemmed_query[0]
                term_postings = postings_collection.find_one({"term": single_term})["positions"]
                result = {doc_id: {single_term: positions} for doc_id, positions in term_postings.items()}
            else:
                first_term = cleaned_and_stemmed_query[0]
                if first_term in postings_collection.distinct("term"):
                    first_term_postings = postings_collection.find_one({"term": first_term})["positions"]
                    for doc_id, positions in first_term_postings.items():
                        final_positions = {term: [] for term in cleaned_and_stemmed_query}
                        # Iterate through the positions of the first term
                        for pos in positions:
                            term_pos = {first_term: pos}
                            match = True
                            # Check if all other terms occur in sequence after the first term
                            for i, term in enumerate(cleaned_and_stemmed_query[1:], start=1):
                                term_postings = postings_collection.find_one({"term": term})["positions"]
                                if doc_id not in term_postings or pos + i not in term_postings[doc_id]:
                                    match = False
                                    break
                                term_pos[term] = pos + i
                            if match:
                                # Add the positions to the final result for each term
                                for term, term_position in term_pos.items():
                                    final_positions[term].append(term_position)
                        # If all terms are present in sequence, add the document to the result
                        if all(len(final_positions[term]) > 0 for term in cleaned_and_stemmed_query):
                            result[doc_id] = final_positions
        except:
            return render(request, 'results.html', {'search_query': search_query})
        # Retrieve the matching documents from your CorpusFile model
        matching_documents = CorpusFile.objects.filter(id__in=result.keys())

                # Calculate file sizes in KB and MB, and format the upload date
        for document in matching_documents:
            file_size_bytes = os.path.getsize(os.path.join(settings.BASE_DIR, 'corpus', document.stored_file_name))
            document.file_size_kb = round(file_size_bytes / 1024, 2)
            document.file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            document.uploaded_date = timezone.localtime(document.uploaded_at).strftime('%Y-%m-%d %H:%M:%S')

        return render(request, 'results.html', {'matching_documents': matching_documents, 'search_query': search_query})
    return render(request, 'search.html')


def results(request):
    pass

def load_image_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    response = FileResponse(document.image, content_type='image/jpeg')  # Assuming image is stored as a FileField
    return response

def view_document(request, doc_id):
    query = request.GET.get('query', '')
    return render(request, 'doc_viewer.html', {'doc_id': doc_id,'query': query})

def load_document(request, doc_id):
    # Get the document object based on the doc_id
    document = get_object_or_404(CorpusFile, id=doc_id)
    query = request.GET.get('query', '')

    if document.stored_file_name.endswith('.pdf'):
        return view_pdf_document(document, query)
    elif document.stored_file_name.endswith(('.doc', '.docx')):
        pass
    elif document.stored_file_name.endswith('.csv'):
        pass
    elif document.stored_file_name.endswith(('.txt', '.text')):
        pass
    elif document.stored_file_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        pass
    elif document.stored_file_name.endswith(('.html', '.htm')):
        pass
    elif document.stored_file_name.endswith(('.gif')):
        pass
    else:
        return ''

def view_pdf_document(document, query):
    pdf_path = os.path.join(settings.BASE_DIR, 'corpus', document.stored_file_name)
    
    # Check if the file exists and is a PDF
    if not os.path.exists(pdf_path) or not pdf_path.endswith('.pdf'):
        return HttpResponseBadRequest("Invalid PDF file.")

    if query:
        pdf_path = highlight_text_in_pdf(pdf_path, document.stored_file_name, query)

    return FileResponse(open(pdf_path, 'rb'))

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
        corpus_file.processed = True
        corpus_file.save()



    












