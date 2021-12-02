from django.urls import path
from . import views

urlpatterns = [
    path('about_company/', views.about_company),
    path('', views.landing),
]