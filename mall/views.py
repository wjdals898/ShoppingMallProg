from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Product, Category, Comment
from .forms import CommentForm

# Create your views here.
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    product = comment.product
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(product.get_absolute_url())
    else:
        raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def new_comment(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.product = product
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(product.get_absolute_url())
    else:
        raise PermissionDenied


class ProductList(ListView):
    model = Product
    ordering = '-pk'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()
        return context

class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_product_count'] = Product.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class ProductSearch(ProductList):
    paginate_by = None
    def get_queryset(self):
        q = self.kwargs['q']
        product_list = Product.objects.filter(
            Q(name__contains=q)
        ).distinct()
        return product_list

    def get_context_data(self, **kwargs):
        context = super(ProductSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'\"{q}\" ?????? ?????? ({self.get_queryset().count()})'
        return context

class ProductCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'content', 'product_color', 'product_size', 'product_image', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            return super(ProductCreate, self).form_valid(form)
        else:
            return redirect('/mall/')

class ProductUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'content', 'product_color', 'product_size', 'product_image', 'category']

    template_name = 'mall/product_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(ProductUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def category_page(request, slug):
    if slug == 'no_category':
        category = '?????????'
        product_list = Product.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        product_list = Product.objects.filter(category=category)

    return render(
        request,
        'mall/product_list.html',
        {
            'product_list': product_list,
            'categories': Category.objects.all(),
            'no_category_product_count': Product.objects.filter(category=None).count(),
            'category': category,
        }
    )



