from django.shortcuts import render
from mall.models import Product

# Create your views here.
def landing(request):
    new_products = Product.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/landing.html',
        {
            'new_products': new_products,
        }
    )

def about_company(request):
    return render(request, 'single_pages/about_company.html')