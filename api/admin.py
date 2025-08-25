from django.contrib import admin
from api.models import Post, UpdateAttachment


class UpdateAttachmentInline(admin.TabularInline):
    model = UpdateAttachment
    extra = 1  # How many empty attachment slots to show
    fields = ('file', 'created_at', 'updated_at')  # Customize visible fields
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    inlines = [UpdateAttachmentInline]  # Attach the inline admin here
