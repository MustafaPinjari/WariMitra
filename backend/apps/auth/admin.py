"""
Django admin configuration for Auth app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TokenRevocation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extended User admin with custom fields"""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'user_type')}),
        ('System', {'fields': ('is_active', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active', 'created_at')
    list_filter = BaseUserAdmin.list_filter + ('user_type', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone_number')


@admin.register(TokenRevocation)
class TokenRevocationAdmin(admin.ModelAdmin):
    """Admin for token revocation audit logs"""
    list_display = ('revocation_id', 'user', 'revoked_by', 'reason', 'created_at', 'is_active')
    list_filter = ('reason', 'created_at', 'is_active')
    search_fields = ('user__username', 'revoked_by__username', 'revocation_id')
    readonly_fields = ('revocation_id', 'created_at', 'updated_at', 'token_hash')
    
    fieldsets = (
        ('Revocation Info', {
            'fields': ('revocation_id', 'user', 'revoked_by', 'reason', 'token_hash')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Status', {
            'fields': ('is_active', 'deleted_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual addition via admin - only programmatic"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent hard delete - only soft delete via is_active"""
        return False
