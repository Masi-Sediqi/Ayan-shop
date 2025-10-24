from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

def shop(request):
    products = Product.objects.prefetch_related('variants__color', 'variants__size').all()

    product_data = []
    for product in products:
        variants = product.variants.all()
        if not variants.exists():
            continue

        first_variant = variants.first()
        colors = []
        for v in variants:
            colors.append({
                'color_name': v.color.name,
                'color_code': v.color.color,
                'image': v.image.url,
                'image_hover': v.image_hover.url,
            })

        product_data.append({
            'product': product,
            'first_variant': first_variant,
            'colors': colors,
        })

    context = {
        'products': product_data
    }
    return render(request, 'products/shop.html', context)

def product_details(request, id):
    product = get_object_or_404(Product, id=id)
    variants = ProductVariant.objects.filter(product=product).select_related('color', 'size')
    default_variant = variants.first()

    colors = Color.objects.filter(productvariant__product=product).distinct()
    sizes = sorted(set(v.size for v in variants), key=lambda s: s.size)

    # --- Handle POST request ---
    if request.method == 'POST':
        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')

        selected_color = Color.objects.filter(id=color_id).first() if color_id else None
        selected_size = Size.objects.filter(id=size_id).first() if size_id else None

        # Determine variant based on selections
        variant = None
        if selected_color and selected_size:
            variant = variants.filter(color=selected_color, size=selected_size).first()
        elif selected_color:
            variant = variants.filter(color=selected_color).first()
        elif selected_size:
            variant = variants.filter(size=selected_size).first()
        else:
            variant = default_variant
    else:
        # GET request or initial load
        variant = default_variant
        selected_color = variant.color if variant else None
        selected_size = variant.size if variant else None

    # --- Collect variant images ---
    variant_images = []
    if variant:
        if variant.image:
            variant_images.append({'url': variant.image.url, 'alt': f"{product.name} main image"})
        if getattr(variant, 'image_hover', None):
            variant_images.append({'url': variant.image_hover.url, 'alt': f"{product.name} hover image"})
        for img in variant.images.all():
            variant_images.append({'url': img.image.url, 'alt': img.alt_text or product.name})

    # --- Discount & price ---
    discount = (
        Discount.objects.filter(variant=variant, active=True).first()
        or Discount.objects.filter(product=product, active=True).first()
        or Discount.objects.filter(category=product.category, active=True).first()
    )

    original_price = variant.price if variant else 0
    final_price = original_price
    discount_percent = 0
    discount_end = None

    if discount:
        if getattr(discount, 'end_date', None):
            discount_end = discount.end_date.isoformat()
        discount_percent = discount.amount
        final_price = original_price - (original_price * discount.amount / 100)

    # get absolute URL for share
    current_site = get_current_site(request)
    product_url = f"http://{current_site.domain}{product.get_absolute_url()}"  # assuming get_absolute_url() exists

    context = {
        'product': product,
        'variants': variants,
        'colors': colors,
        'sizes': sizes,
        'variant_images': variant_images,
        'selected_color': selected_color,
        'selected_size': selected_size,
        'original_price': original_price,
        'final_price': final_price,
        'discount_percent': discount_percent,
        'discount_end': discount_end,
        'product_url': product_url,
        'variant': variant,   # ✅ add this line
    }
    return render(request, 'products/product_detail.html', context)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Get all products of this category
    products = category.products.all()  # Assuming Product has FK to Category

    product_data = []
    for product in products:
        variants = product.variants.all()
        if not variants.exists():
            continue

        # pick one variant per product to show in main listing
        first_variant = variants.filter(show_in_main_page=True).first() or variants.first()

        # get all colors
        colors = [{
            'color_name': v.color.name,
            'color_code': getattr(v.color, 'color', '#000'),
            'image': v.image.url,
            'image_hover': v.image_hover.url
        } for v in variants]

        # get all sizes
        sizes = [v.size.size for v in variants]

        # price/discount
        discount = (
            Discount.objects.filter(variant=first_variant, active=True).first()
            or Discount.objects.filter(product=product, active=True).first()
            or Discount.objects.filter(category=category, active=True).first()
        )
        original_price = first_variant.price
        if discount:
            final_price = first_variant.price - (first_variant.price * discount.amount / 100)
        else:
            final_price = first_variant.price

        product_data.append({
            'product': product,
            'first_variant': first_variant,
            'colors': colors,
            'sizes': sizes,
            'original_price': original_price,
            'final_price': final_price,
            'has_discount': discount is not None,
        })

    context = {
        'category': category,
        'products': product_data,
    }

    return render(request, 'category/products.html', context)

@login_required
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    if user in product.liked_by.all():
        product.liked_by.remove(user)
        liked = False
    else:
        product.liked_by.add(user)
        liked = True

    return redirect('products:product_details', id=product.id)