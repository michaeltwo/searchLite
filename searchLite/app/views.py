from django.shortcuts import render
from django.http import HttpResponse

def example_view(request):
    
    # Perform your search logic here
    # For demonstration purposes, we'll just return the query
    return render(request, 'index.html')

