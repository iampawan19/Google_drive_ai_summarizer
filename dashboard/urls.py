"""
Dashboard URLs
Routes for the dashboard app
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('summarize/', views.summarize, name='summarize'),
    path('download-csv/', views.download_csv, name='download_csv'),
]
