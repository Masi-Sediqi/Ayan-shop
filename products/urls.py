from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path('shop', views.shop, name="shop"),
    path('product/<int:id>/', views.product_details, name='product_details'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/like/', views.toggle_like, name='toggle_like'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('user/<int:user_id>/wishlist/', views.user_wishlist, name='user_wishlist'),
]