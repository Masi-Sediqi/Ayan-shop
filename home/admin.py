from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'address')
    search_fields = ('email', 'phone_number', 'address')


@admin.register(ContactUsMessages)
class ContactUsMessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'text')
    search_fields = ('name', 'email', 'phone', 'text')
    list_filter = ('email',)

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title',)  # show title in list view
    search_fields = ('title', 'details')  # allow searching by title or details

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at', 'updated_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;">', obj.image.url)
        return "No image"
    image_preview.short_description = "Image"

@admin.register(BlogReply)
class BlogReplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'created_at')
    search_fields = ('name', 'reply_text')

@admin.register(SocialMediaLinks)
class SocialMediaLinksAdmin(admin.ModelAdmin):
    list_display = ('whatsapp', 'instagram', 'tiktok')