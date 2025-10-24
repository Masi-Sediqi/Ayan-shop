from django.shortcuts import render
from products.models import *
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import OuterRef, Subquery
# Create your views here.
def home(request):
    categories = Category.objects.all()
    category_data = []

    for cate in categories:
        discount = Discount.objects.filter(category=cate, active=True, end_date__gte=timezone.now()).first()
        discount_percent = discount.amount if discount and discount.discount_type == 'percent' else 0
        category_data.append({
            'category': cate,
            'discount_percent': discount_percent,
        })

    main_categories = MainCategory.objects.prefetch_related('categories').all()
    single_categories = Category.objects.filter(main_category__isnull=True)

    # Get variants marked for main page
    marked_variants = ProductVariant.objects.filter(show_in_main_page=True).select_related('product', 'color', 'size')

    # Group by product
    products = []
    for variant in marked_variants:
        product = variant.product
        all_variants = ProductVariant.objects.filter(product=product)

        # Colors
        colors = [{
            'name': v.color.name,
            'code': getattr(v.color, 'color', '#000'),  # fallback if no color code
            'image': v.image.url,
            'image_hover': v.image_hover.url
        } for v in all_variants]

        # Sizes
        sizes = [v.size.size for v in all_variants]

        # Price and discount
        discount = (
            Discount.objects.filter(variant=variant, active=True).first()
            or Discount.objects.filter(product=product, active=True).first()
            or Discount.objects.filter(category=product.category, active=True).first()
        )
        original_price = variant.price
        if discount:
            final_price = variant.price - (variant.price * discount.amount / 100)
        else:
            final_price = variant.price

        products.append({
            'product': product,
            'first_variant': variant,
            'colors': colors,
            'sizes': sizes,
            'original_price': original_price,
            'final_price': final_price,
            'has_discount': discount is not None,
        })

    context = {
        'categories': category_data,
        'main_categories': main_categories,
        'single_categories': single_categories,
        'marked_products': products,
    }

    return render(request, 'index.html', context)