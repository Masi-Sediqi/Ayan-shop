from django.shortcuts import render
from products.models import *
from django.utils import timezone
# Create your views here.

def home(request):
    categories = Category.objects.all()
    category_data = []

    for cate in categories:
        # Get the active discount for this category
        discount = Discount.objects.filter(category=cate, active=True, end_date__gte=timezone.now()).first()
        discount_percent = discount.amount if discount and discount.discount_type == 'percent' else 0

        category_data.append({
            'category': cate,
            'discount_percent': discount_percent,
        })

    context = {
        'categories': category_data,
    }
    return render(request, 'index.html', context)