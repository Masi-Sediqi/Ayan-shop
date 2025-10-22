from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import HttpResponse
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
    }
    return render(request, 'products/product_detail.html', context)