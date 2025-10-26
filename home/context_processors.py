from products.models import *
from .models import *

def categories_context(request):
    main_categories = MainCategory.objects.prefetch_related('categories').all()
    single_categories = Category.objects.filter(main_category__isnull=True)
    six_first_category = Category.objects.all().order_by('id')[:6]
    social_media_links = SocialMediaLinks.objects.last()
    contact_us = ContactUs.objects.last()
    about_us = AboutUs.objects.last()

    user = request.user
    if user.is_authenticated:
        user_liked_products = Product.objects.filter(liked_by=user)
        liked_count = user_liked_products.count()
    else:
        user_liked_products = Product.objects.none()  # empty queryset
        liked_count = 0
    
    return {
        'main_categories': main_categories,
        'single_categories': single_categories,
        'user_liked_products': user_liked_products,
        'liked_count': liked_count,
        'six_first_category': six_first_category,
        'social_media_links': social_media_links,
        'contact_us': contact_us,
        'about_us': about_us,
    }