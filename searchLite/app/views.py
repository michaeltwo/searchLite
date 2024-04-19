from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
    # Perform your search logic here
    # For demonstration purposes, we'll just return the query
    return render(request, 'index.html')

def upload(request):
    return render(request, 'upload.html')  

def search(request):
    return render(request, 'search.html')  
