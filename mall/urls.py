from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:q>/', views.ProductSearch.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('update_product/<int:pk>/', views.ProductUpdate.as_view()),
    path('create_product/', views.ProductCreate.as_view()),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/new_comment/', views.new_comment),
    path('<int:pk>/', views.ProductDetail.as_view()),
    path('', views.ProductList.as_view()),
]