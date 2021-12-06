from django.urls import path
from . import views

urlpatterns = [
    path('create_product/', views.ProductCreate.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.ProductDetail.as_view()),
    path('', views.ProductList.as_view()),
]