from django.urls import path
from . import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('', views.homepage, name='homepage'),
    path('upload/', views.upload, name='upload'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('load/<int:document_id>/', views.load_document_image, name='load_document_image'),
]
