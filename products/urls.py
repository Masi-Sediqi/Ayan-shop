from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path('shop', views.shop, name="shop"),
    path('product/<int:id>/', views.product_details, name='product_details'),
]