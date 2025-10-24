from django.contrib import admin
import admin_thumbnails
from .models import *

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "main_category", "slug")
    list_filter = ("main_category",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "main_category__name")

# Thumbnail preview only for the image inline
@admin_thumbnails.thumbnail('image')
class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    readonly_fields = ('id',)
    extra = 1  # show 1 empty image fields by default


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 1
    show_change_link = True
    fields = ['size', 'color', 'price', 'stock']
    inlines = [ProductVariantImageInline]  # images inline under each variant


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'created_at']
    search_fields = ['name', 'brand']
    inlines = [ProductVariantInline]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'size']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'price', 'stock']
    list_filter = ['product', 'size', 'color']
    search_fields = ['product__name', 'size__name', 'color__name']
    inlines = [ProductVariantImageInline]  # images inline in variant admin


# ❌ remove this — do NOT register ProductVariantImage separately
# @admin.register(ProductVariantImage)
# class ProductVariantImageAdmin(admin.ModelAdmin):
#     list_display = ['id', 'variant', 'alt_text', 'image']
#     readonly_fields = ('id',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name',  'amount', 'active', 'start_date', 'end_date']
    list_filter = [ 'active', 'start_date', 'end_date']
    search_fields = ['name']