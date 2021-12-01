from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

# Create your views here.
class ProductList(ListView):
    model = Product
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductList, self).get_context_data()
        return context
