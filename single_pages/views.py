from django.shortcuts import render
from mall.models import Product

# Create your views here.
def landing(request):
    #recent_posts = Product.objects.order_by('-pk')[:3]
    return render(request, 'single_pages/landing.html')
                  #,{'recent_posts' : recent_posts})

def about_company(request):
    return render(request, 'single_pages/about_company.html')