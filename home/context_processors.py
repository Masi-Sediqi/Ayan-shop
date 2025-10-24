from products.models import *

def categories_context(request):
    main_categories = MainCategory.objects.prefetch_related('categories').all()
    single_categories = Category.objects.filter(main_category__isnull=True)

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
    }