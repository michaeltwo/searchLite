from django.urls import path
from . import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('', views.homepage, name='homepage'),
    path('upload/', views.upload, name='upload'),
    path('search/', views.search, name='search'),
]
