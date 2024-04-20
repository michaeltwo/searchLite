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
    valid_files = []
    invalid_files = []
    
    if request.method == 'POST' and request.FILES.getlist('file'):
        files = request.FILES.getlist('file')
        for file in files:
            file_info = filetype.guess(file.read())
            if file_info is not None and file_info.mime in ALLOWED_FILE_TYPES:
                file_hash = generate_file_hash(file)
                if file_hash:
                    if not CorpusFile.objects.filter(file_hash=file_hash).exists():
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        stored_file_name = f"{file.name}_{timestamp}"
                        file_path = os.path.join(settings.BASE_DIR, 'corpus', stored_file_name)
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
                        valid_files.append(file.name)
                    else:
                        invalid_files.append(f"{file.name} (duplicate file)")
                else:
                    invalid_files.append(f"{file.name} (error generating hash)")
            else:
                invalid_files.append(f"{file.name} (invalid file type)")
        
        message = ''
        if valid_files:
            message += f"Files uploaded successfully: {', '.join(valid_files)}. "
        if invalid_files:
            message += f"Invalid files: {', '.join(invalid_files)}"
        
        return render(request, 'upload.html', {'message': message})
    
    return render(request, 'upload.html')



def search(request):
    return render(request, 'search.html')  


def generate_file_hash(file):
    try:
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        return file_hash
    except Exception as e:
        print(f"Error generating file hash: {e}")
        return None