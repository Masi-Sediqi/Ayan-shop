from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField
# Create your models here.

class ContactUs(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=400)

class ContactUsMessages(models.Model):
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(blank=True)
    phone = models.IntegerField(blank=True)
    text = models.TextField(blank=False)

class AboutUs(models.Model):
    title = models.CharField(max_length=300)
    details = models.TextField()
    image = models.ImageField(upload_to="about_us/")
    second_image = models.ImageField(upload_to="about_us/")
    three_image = models.ImageField(upload_to="about_us/")
    fourth_image = models.ImageField(upload_to="about_us/")
    slogan = models.CharField(max_length=200, verbose_name="شعار")

class BlogCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="blogs/")
    short_description = models.CharField(max_length=400, blank=True)
    content = RichTextField()  # ✅ replaces TextField
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100, blank=False)
    image = models.ImageField(blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class BlogReply(models.Model):
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name="replies")
    name = models.CharField(max_length=100, blank=False)
    image = models.ImageField(blank=True)
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.name} on {self.comment.name}'s comment"
    
class SocialMediaLinks(models.Model):
    whatsapp = models.URLField()
    instagram = models.URLField()
    tiktok = models.URLField()

    def __str__(self):
        return f"Whatsapp {self.whatsapp} Instagram {self.instagram} TikTok {self.tiktok}"