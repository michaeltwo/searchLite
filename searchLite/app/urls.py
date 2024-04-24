from django.urls import path
from . import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('', views.homepage, name='homepage'),
    path('upload/', views.upload, name='upload'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('load/<int:document_id>/', views.load_document_image, name='load_document_image'),
    path('view/<int:doc_id>', views.view_document, name='view_document'),
    path('view_pdf_document/<int:doc_id>/', views.view_pdf_document, name='view_pdf_document'),
    path('view_document_image/<int:doc_id>/', views.view_document_image, name='view_document_image'),
    path('load_document/<int:doc_id>/', views.load_document, name='load_document'),
]
