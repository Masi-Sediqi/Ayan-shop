from django.shortcuts import render, redirect, get_object_or_404
from products.models import *
from django.utils import timezone
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.db.models import Q
# Create your views here.
def home(request):
    categories = Category.objects.all()
    blog_record = Blog.objects.filter(is_published=True)
    category_data = []

    for cate in categories:
        discount = Discount.objects.filter(category=cate, active=True, end_date__gte=timezone.now()).first()
        discount_percent = discount.amount if discount and discount.discount_type == 'percent' else 0

        product_count = Product.objects.filter(category=cate).count()
    
        category_data.append({
            'category': cate,
            'discount_percent': discount_percent,
            'product_count': product_count,
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
        'blog_record': blog_record,
    }

    return render(request, 'index.html', context)

def contact_us(request):
    try:
        contact_info = ContactUs.objects.last()
    except:
        contact_info = None

    if request.method == 'POST':
        name = request.POST.get('fname', '').strip()
        email = request.POST.get('umail', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        if name and message:
            ContactUsMessages.objects.create(
                name=name,
                email=email,
                phone=int(phone) if phone.isdigit() else None,
                text=message
            )
            messages.success(request, "Your message has been sent successfully!")

    return render(request, 'home/contact-us.html', {
        'contact_info': contact_info,
    })

def about_us(request):
    try:
        about_info = AboutUs.objects.last()
    except:
        about_info = None
    return render(request, 'home/about-us.html', {'about_info':about_info})

def blog(request):
    blogs_record = Blog.objects.filter(is_published=True)

    context = {
        'blogs_record':blogs_record
    }
    return render(request, 'home/blog.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    blog_comments = BlogComment.objects.filter(blog=blog).order_by('-created_at')

    # Handle new comment submission
    if request.method == "POST":
        if "comment_submit" in request.POST and request.FILES:
            name = request.POST.get("name")
            comment_text = request.POST.get("comment")
            image = request.FILES.get("image")

            if name and comment_text:
                BlogComment.objects.create(blog=blog, name=name, comment=comment_text, image=image)
            return redirect("home:blog_detail", slug=slug)
        
    return render(request, "home/blog_detail.html", {
        "blog": blog,
        "blog_comments": blog_comments,
    })

def comment_reply(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        name = request.POST.get("name")
        reply_text = request.POST.get("reply_text")
        image = request.FILES.get("image")  # optional

        if not comment_id or not name or not reply_text:
            messages.error(request, "All required fields must be filled!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Find the base comment
        comment = get_object_or_404(BlogComment, id=comment_id)

        # Create reply
        reply = BlogReply.objects.create(
            comment=comment,
            name=name,
            reply_text=reply_text,
            image=image if image else None
        )
        messages.success(request, "Reply submitted successfully!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # If GET or other method
    return redirect(request.META.get('HTTP_REFERER', '/'))

def product_search(request):
    query = request.GET.get("q")
    print(query)  # for debugging
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('category')[:10]

        if request.user.is_authenticated:
            if not RecentSearch.objects.filter(user=request.user, query=query).exists():
                RecentSearch.objects.create(user=request.user, query=query)

    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = request.user.recent_searches.all()[:5]

    return render(request, "partials/search_results.html", {
        "results": results,
        "recent_searches": recent_searches
    })

def search_blog(request):
    query = request.GET.get("q")
    print(query)  # for debugging
    if query:
        results = Blog.objects.filter(Q(title__icontains=query) | Q(short_description__icontains=query) | Q(content__icontains=query))[:5]

    return render(request, "partials/blog_search_results.html", {
        "results": results,
    })