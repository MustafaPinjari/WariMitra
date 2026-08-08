"""
Django Admin Configuration for SOS Module
Phase 1.2 Implementation: DDoS Protection

Provides read-only admin interfaces for auditing and monitoring SOS activities.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SosAlert, DeviceFingerprint, SOSAuditLog


@admin.register(SosAlert)
class SosAlertAdmin(admin.ModelAdmin):
    """Admin interface for SOS Alerts"""
    
    list_display = [
        'id',
        'user',
        'status',
        'severity_badge',
        'latitude',
        'longitude',
        'created_at',
    ]
    list_filter = [
        'status',
        'severity',
        'created_at',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'id',
    ]
    readonly_fields = [
        'id',
        'user',
        'status',
        'latitude',
        'longitude',
        'description',
        'severity',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('id', 'user', 'status', 'severity')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable adding new alerts from admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting alerts from admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing alerts from admin"""
        return False
    
    def severity_badge(self, obj):
        """Display severity as color-coded badge"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    """Admin interface for Device Fingerprints"""
    
    list_display = [
        'fingerprint_short',
        'ip_address',
        'device_model',
        'app_version',
        'created_at',
    ]
    list_filter = [
        'device_model',
        'app_version',
        'created_at',
    ]
    search_fields = [
        'fingerprint',
        'ip_address',
        'device_model',
    ]
    readonly_fields = [
        'fingerprint',
        'ip_address',
        'user_agent',
        'device_model',
        'app_version',
        'os_version',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Fingerprint', {
            'fields': ('fingerprint',)
        }),
        ('Device Information', {
            'fields': ('device_model', 'app_version', 'os_version')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable adding fingerprints from admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting fingerprints from admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing fingerprints from admin"""
        return False
    
    def fingerprint_short(self, obj):
        """Display shortened fingerprint"""
        return f"{obj.fingerprint[:16]}..."
    fingerprint_short.short_description = 'Fingerprint'


@admin.register(SOSAuditLog)
class SOSAuditLogAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for SOS Audit Logs.
    
    Provides comprehensive audit trail view for compliance and security monitoring.
    Includes filtering, searching, and colorized result display.
    """
    
    list_display = [
        'id',
        'result_badge',
        'device_fingerprint_short',
        'ip_address',
        'rate_limits_status',
        'geofence_status_badge',
        'created_at',
    ]
    list_filter = [
        'result',
        'rate_limit_ip_status',
        'rate_limit_device_status',
        'geofence_status',
        'created_at',
    ]
    search_fields = [
        'device_fingerprint',
        'ip_address',
        'sos_alert_id',
        'user__username',
    ]
    readonly_fields = [
        'sos_alert',
        'device_fingerprint',
        'device_model',
        'app_version',
        'ip_address',
        'user_agent',
        'latitude',
        'longitude',
        'radius',
        'rate_limit_ip_status',
        'rate_limit_device_status',
        'geofence_status',
        'result',
        'reason',
        'user',
        'created_at',
        'deleted_at',
        'is_active',
    ]
    
    fieldsets = (
        ('Attempt Result', {
            'fields': ('result', 'reason', 'created_at')
        }),
        ('Alert Reference', {
            'fields': ('sos_alert', 'user'),
            'classes': ('collapse',)
        }),
        ('Device Information', {
            'fields': (
                'device_fingerprint',
                'device_model',
                'app_version',
            ),
        }),
        ('Network Information', {
            'fields': ('ip_address', 'user_agent'),
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude', 'radius'),
        }),
        ('DDoS Protection Checks', {
            'fields': (
                'rate_limit_ip_status',
                'rate_limit_device_status',
                'geofence_status',
            ),
            'description': (
                'Status of each DDoS protection check performed'
            ),
        }),
        ('Soft Delete', {
            'fields': ('is_active', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable adding audit logs from admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable permanent deletion - only soft delete"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs - must be immutable"""
        return False
    
    def result_badge(self, obj):
        """Display result as color-coded badge"""
        colors = {
            'SUCCESS': '#28a745',
            'RATE_LIMITED_IP': '#ffc107',
            'RATE_LIMITED_DEVICE': '#ffc107',
            'INVALID_LOCATION': '#fd7e14',
            'INVALID_FINGERPRINT': '#fd7e14',
            'ERROR': '#dc3545',
        }
        color = colors.get(obj.result, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_result_display()
        )
    result_badge.short_description = 'Result'
    
    def device_fingerprint_short(self, obj):
        """Display shortened device fingerprint"""
        return f"{obj.device_fingerprint[:12]}..."
    device_fingerprint_short.short_description = 'Device FP'
    
    def rate_limits_status(self, obj):
        """Display both rate limit statuses"""
        statuses = []
        
        # IP rate limit
        if obj.rate_limit_ip_status == 'REJECT':
            statuses.append(format_html(
                '<span style="color: #dc3545; font-weight: bold;">IP ✗</span>'
            ))
        elif obj.rate_limit_ip_status == 'WARN':
            statuses.append(format_html(
                '<span style="color: #ffc107; font-weight: bold;">IP ⚠</span>'
            ))
        
        # Device rate limit
        if obj.rate_limit_device_status == 'REJECT':
            statuses.append(format_html(
                '<span style="color: #dc3545; font-weight: bold;">DEV ✗</span>'
            ))
        elif obj.rate_limit_device_status == 'WARN':
            statuses.append(format_html(
                '<span style="color: #ffc107; font-weight: bold;">DEV ⚠</span>'
            ))
        
        if statuses:
            return format_html(' '.join([str(s) for s in statuses]))
        else:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">All Pass ✓</span>'
            )
    rate_limits_status.short_description = 'Rate Limits'
    
    def geofence_status_badge(self, obj):
        """Display geofence status as badge"""
        if obj.geofence_status == 'REJECT':
            color = '#dc3545'
            icon = '✗'
        else:
            color = '#28a745'
            icon = '✓'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            icon
        )
    geofence_status_badge.short_description = 'Geofence'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'sos_alert',
            'user'
        )
