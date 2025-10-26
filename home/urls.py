from django.urls import path
from .import views

app_name = "home"

urlpatterns = [
    path('', views.home, name='home'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('about_us', views.about_us, name='about_us'),
    path('blog', views.blog, name='blog'),
    path('comment_reply', views.comment_reply, name='comment_reply'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('search/', views.product_search, name='product_search'),
]