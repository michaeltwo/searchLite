from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .constants import ALLOWED_FILE_TYPES
from .models import CorpusFile
from datetime import datetime
import filetype
import hashlib
import os

def homepage(request):
    # Perform your search logic here
    # For demonstration purposes, we'll just return the query
    return render(request, 'index.html')


def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        file_info = filetype.guess(file.read())
        if file_info is not None and file_info.mime in ALLOWED_FILE_TYPES:
            file_hash = generate_file_hash(file_path)
            if file_hash:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                stored_file_name = f"{file.name}_{timestamp}"
                file_path = os.path.join(settings.BASE_DIR, 'corpus', stored_file_name)
                if not CorpusFile.objects.filter(file_hash=file_hash).exists():
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    uploaded_file = CorpusFile(
                        uploaded_file_name=file.name,
                        stored_file_name=stored_file_name,
                        file_type=file_info.mime,
                        file_size=file.size,
                        file_hash=file_hash
                    )
                    uploaded_file.save()
                    return render(request, 'upload.html', {'message': 'File uploaded successfully'})
                else:
                    return render(request, 'upload.html', {'message': 'File already exists.'})
            else:
                return render(request, 'upload.html', {'message': 'Error generating file hash.'})
        else:
            return render(request, 'upload.html', {'message': 'Invalid file type. Only JPG, JPEG, BMP, DOC, DOCX, CSV, PDF, and TXT files are allowed.'})
    return render(request, 'upload.html')



def search(request):
    return render(request, 'search.html')  


def generate_file_hash(file_path):
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            return file_hash
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        return None