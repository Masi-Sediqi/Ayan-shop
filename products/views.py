from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max
# Create your views here.

def shop(request):
    products = Product.objects.prefetch_related('variants__color', 'variants__size').all()
    is_filter = None
    categories = Category.objects.all()
    sizes = Size.objects.all()
    colors = Color.objects.all()
    price_range = products.aggregate(min_price=Min('variants__price'), max_price=Max('variants__price'))

    # Handle filters
    if request.method == "POST":
        category_ids = request.POST.getlist("category")
        size_ids = request.POST.getlist("size")
        color_ids = request.POST.getlist("color")
        min_price = request.POST.get("min_price")
        max_price = request.POST.get("max_price")

        filters = Q()

        # 🎯 Step 1 — Apply price filter (main condition)
        if min_price and max_price:
            filters &= Q(variants__price__gte=min_price, variants__price__lte=max_price)
        elif min_price:
            filters &= Q(variants__price__gte=min_price)
        elif max_price:
            filters &= Q(variants__price__lte=max_price)

        # Step 2 — Apply other filters *only inside* the price range (optional)
        products = products.filter(filters).distinct()
        is_filter = True

        # Optional refinements
        if category_ids:
            products = products.filter(category__id__in=category_ids)
        if size_ids:
            products = products.filter(variants__size__id__in=size_ids)
        if color_ids:
            products = products.filter(variants__color__id__in=color_ids)

        products = products.distinct()

    # Prepare product data
    product_data = []
    for product in products:
        variants = product.variants.all()
        if not variants.exists():
            continue

        first_variant = variants.first()
        colors_list = [{
            'id': v.color.id,
            'color_name': v.color.name,
            'color_code': v.color.color,
            'image': v.image.url,
            'image_hover': v.image_hover.url,
        } for v in variants]

        sizes_list = list(set(v.size for v in variants))

        product_data.append({
            'product': product,
            'first_variant': first_variant,
            'colors': colors_list,
            'sizes': sizes_list,
        })

    context = {
        'products': product_data,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'price_range': price_range,
        'selected_categories': [int(x) for x in request.POST.getlist("category")],
        'selected_sizes': [int(x) for x in request.POST.getlist("size")],
        'selected_colors': [int(x) for x in request.POST.getlist("color")],
        'selected_min_price': request.POST.get("min_price", ""),
        'selected_max_price': request.POST.get("max_price", ""),
        'is_filter': is_filter,
    }

    return render(request, 'products/shop.html', context)

def product_details(request, id):
    product = get_object_or_404(Product, id=id)
    try:
        product_reviews = Reviews.objects.filter(product=product)
    except:
        product_reviews = Reviews.objects.none()

    variants = ProductVariant.objects.filter(product=product).select_related('color', 'size')
    default_variant = variants.first()

    product_colors = Color.objects.filter(productvariant__product=product).distinct()
    product_sizes = sorted(set(v.size for v in variants), key=lambda s: s.size)

    # --- Handle POST request ---
    if request.method == 'POST':
        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')

        selected_color = Color.objects.filter(id=color_id).first() if color_id else None
        selected_size = Size.objects.filter(id=size_id).first() if size_id else None

        # Determine variant based on selections
        main_variant = None
        if selected_color and selected_size:
            main_variant = variants.filter(color=selected_color, size=selected_size).first()
        elif selected_color:
            main_variant = variants.filter(color=selected_color).first()
        elif selected_size:
            main_variant = variants.filter(size=selected_size).first()
        else:
            main_variant = default_variant
    else:
        # GET request or initial load
        main_variant = default_variant
        selected_color = main_variant.color if main_variant else None
        selected_size = main_variant.size if main_variant else None

    # --- Collect variant images ---
    variant_images = []
    if main_variant:
        if main_variant.image:
            variant_images.append({'url': main_variant.image.url, 'alt': f"{product.name} main image"})
        if getattr(main_variant, 'image_hover', None):
            variant_images.append({'url': main_variant.image_hover.url, 'alt': f"{product.name} hover image"})
        for img in main_variant.images.all():
            variant_images.append({'url': img.image.url, 'alt': img.alt_text or product.name})

    # --- Discount & price ---
    main_discount = (
        Discount.objects.filter(variant=main_variant, active=True).first()
        or Discount.objects.filter(product=product, active=True).first()
        or Discount.objects.filter(category=product.category, active=True).first()
    )

    original_price = main_variant.price if main_variant else 0
    final_price = original_price
    discount_percent = 0
    discount_end = None

    if main_discount:
        if getattr(main_discount, 'end_date', None):
            discount_end = main_discount.end_date.isoformat()
        discount_percent = main_discount.amount
        final_price = original_price - (original_price * main_discount.amount / 100)

    # --- Related products ---
    related_variants = ProductVariant.objects.filter(
        product__category=product.category
    ).exclude(product=product).select_related('product', 'color', 'size')

    related_products = []
    seen_ids = set()

    for rel_var in related_variants:
        rel_prod = rel_var.product
        if rel_prod.id not in seen_ids:
            all_variants = ProductVariant.objects.filter(product=rel_prod)

            # Colors for related product
            rel_colors = [{
                'name': v.color.name,
                'code': getattr(v.color, 'color', '#000'),
                'image': v.image.url if v.image else '',
                'image_hover': v.image_hover.url if getattr(v, 'image_hover', None) else ''
            } for v in all_variants]

            # Sizes for related product
            rel_sizes = [v.size.size for v in all_variants if v.size]

            # Price & discount for related product
            rel_discount = (
                Discount.objects.filter(variant=rel_var, active=True).first()
                or Discount.objects.filter(product=rel_prod, active=True).first()
                or Discount.objects.filter(category=rel_prod.category, active=True).first()
            )
            rel_original_price = rel_var.price
            rel_final_price = rel_original_price
            if rel_discount:
                rel_final_price = rel_original_price - (rel_original_price * rel_discount.amount / 100)

            related_products.append({
                'product': rel_prod,
                'first_variant': rel_var,
                'colors': rel_colors,
                'sizes': rel_sizes,
                'original_price': rel_original_price,
                'final_price': rel_final_price,
                'has_discount': rel_discount is not None,
            })

            seen_ids.add(rel_prod.id)

    # get absolute URL for share
    current_site = get_current_site(request)
    product_url = f"http://{current_site.domain}{product.get_absolute_url()}"

    context = {
        'product': product,
        'variants': variants,
        'colors': product_colors,
        'sizes': product_sizes,
        'variant_images': variant_images,
        'selected_color': selected_color,
        'selected_size': selected_size,
        'original_price': original_price,
        'final_price': final_price,
        'discount_percent': discount_percent,
        'discount_end': discount_end,
        'product_url': product_url,
        'variant': main_variant,
        'product_reviews': product_reviews,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)

def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        name = request.POST.get('your-name')
        comment = request.POST.get('your-commemt')
        rating = int(request.POST.get('rating', 5))
        image = request.FILES.get('your-image')  # 🖼️ Get uploaded image

        Reviews.objects.create(
            product=product,
            name=name,
            detail=comment,
            rating=rating,
            image=image
        )
        messages.success(request, "Your review has been submitted successfully!")
        return redirect('products:product_details', id=product.id)
    
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()  # initial queryset

    if request.method == 'POST':
    
        size_ids = request.POST.get('size')
        print(size_ids)
        color_ids = request.POST.get('color')
        print(color_ids)
        min_price = request.POST.get('min_price')
        print(min_price)
        max_price = request.POST.get('max_price')
        print(max_price)

        if size_ids:
            products = products.filter(variants__size__id__in=size_ids).distinct()
        if color_ids:
            products = products.filter(variants__color__id__in=color_ids).distinct()
        if min_price:
            products = products.filter(variants__price__gte=min_price).distinct()
        if max_price:
            products = products.filter(variants__price__lte=max_price).distinct()

    # Prepare product data
    product_data = []
    for product in products:
        variants = product.variants.all()
        if not variants.exists():
            continue
        first_variant = variants.filter(show_in_main_page=True).first() or variants.first()

        colors = [{
            'color_name': v.color.name,
            'color_code': getattr(v.color, 'color', '#000'),
            'image': v.image.url,
            'image_hover': v.image_hover.url
        } for v in variants]

        sizes = [v.size.size for v in variants]

        discount = (
            Discount.objects.filter(variant=first_variant, active=True).first()
            or Discount.objects.filter(product=product, active=True).first()
            or Discount.objects.filter(category=category, active=True).first()
        )
        original_price = first_variant.price
        final_price = original_price
        if discount:
            final_price = original_price - (original_price * discount.amount / 100)

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
        'sizes': Size.objects.all(),
        'colors': Color.objects.all(),
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

@login_required
def user_wishlist(request, user_id):
    user_wishlist_products = Product.objects.filter(liked_by=user_id).prefetch_related('variants')

    wishlist_data = []

    for product in user_wishlist_products:
        # pick one variant to show
        first_variant = product.variants.filter(show_in_main_page=True).first() or product.variants.first()
        if not first_variant:
            continue

        wishlist_data.append({
            'product': product,
            'variant': first_variant,
            'price': first_variant.price,
            'image': first_variant.image.url,
            'stock': first_variant.stock,
            'size': first_variant.size.size if first_variant.size else None,
            'color': first_variant.color.name if first_variant.color else None,
        })

    context = {
        'wishlist_data': wishlist_data,
    }
    return render(request, 'products/user_product_wishlist.html', context)