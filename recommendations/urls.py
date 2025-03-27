# recommendations/urls.py

from django.urls import path
from .views import test_view,recommend_view

urlpatterns = [
    path('test/', test_view, name='test'),
]
from .views import test_view, recommend_view

urlpatterns = [
    path('test/', test_view, name='test'),
    path('recommend/', recommend_view, name='recommend'),  #new endpoint
]
