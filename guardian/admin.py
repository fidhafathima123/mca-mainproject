from django.contrib import admin

# Register your models here.
# guardian/admin.py
from django.contrib import admin
from .models import Guardian

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'get_email')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('user__is_active',)
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
    )