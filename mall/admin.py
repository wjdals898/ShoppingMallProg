from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Product, Category, Comment

# Register your models here.
admin.site.register(Product, MarkdownxModelAdmin)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment)