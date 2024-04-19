from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

def example_view(request):
    
    # Perform your search logic here
    # For demonstration purposes, we'll just return the query
    return render(request, 'index.html')


    
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        file_path = os.path.join(settings.BASE_DIR, 'corpus', file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return render(request, 'upload.html', {'message': 'File uploaded successfully'})
    return render(request, 'upload.html')

