from django.urls import path
from . import views

urlpatterns = [
    path('about_company/', views.about_company),
    path('my_page/', views.mypage),
    path('', views.landing),
]