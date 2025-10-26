from django.db import models
from colorfield.fields import ColorField
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    icon = models.ImageField(upload_to="icon_images", blank=False)

    class Meta:
        verbose_name_plural = 'Main Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.CASCADE,
        related_name='categories',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    second_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    third_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.ImageField(upload_to="icon_images", blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ('main_category', 'name')

    def __str__(self):
        return f"→ {self.name}"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    show_in_main_page = models.BooleanField(default=False)  

    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_products')

    def __str__(self):
        return self.name

    def total_likes(self):
        return self.liked_by.count()

    
    def get_absolute_url(self):
        return reverse('products:product_details', args=[self.id])

class Size(models.Model):
    name = models.CharField(max_length=50)
    size = models.CharField(max_length=50)

    def __str__(self):
        return self.size


class Color(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#000000')

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/main/")
    image_hover = models.ImageField(upload_to="products/main/")
    stock = models.PositiveIntegerField(default=0)
    show_in_main_page = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} - {self.size.name} - {self.color.name}"


class ProductVariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/variants/')
    alt_text = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.variant}"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    # apply discount to specific items (optional)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.amount})"

    def is_valid(self):
        """Check if discount is active and in date range"""
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def apply_discount(self, price):
        """Return discounted price"""
        if not self.is_valid():
            return price

        return price - (price * (self.amount / 100))
    
class Reviews(models.Model):
    product = models.ForeignKey(
        Product,  # assuming you have a Product model
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    name = models.CharField(max_length=100, blank=False)
    image = models.ImageField(upload_to="products/reviews", blank=True)
    detail = models.TextField()
    
    rating = models.PositiveIntegerField(default=5) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.product.name} ({self.rating}⭐)"
    
class RecentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recent_searches')
    query = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.query