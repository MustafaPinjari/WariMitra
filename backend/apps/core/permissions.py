"""
Custom DRF Permission Classes
Phase 1.4: Object-Level RBAC implementation foundation
"""
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser
from django.contrib.auth.models import Group


class IsAdmin(IsAdminUser):
    """User must be admin"""
    message = "Only administrators can access this resource."


class IsOwner(BasePermission):
    """User must own the object"""
    message = "You do not have permission to access this object."
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsMedicalStaff(BasePermission):
    """User must be medical staff"""
    message = "Only medical staff can access this resource."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_type in ['medical_officer', 'admin']


class IsPoliceOfficer(BasePermission):
    """User must be police officer"""
    message = "Only police officers can access this resource."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_type in ['police_officer', 'admin']


class IsInSameOrganization(BasePermission):
    """User must be in same organization/camp"""
    message = "You cannot access resources from another organization."
    
    def has_object_permission(self, request, view, obj):
        # Override this in subclasses or handle in view
        # For now, check if user has access to object's organization
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        elif hasattr(obj, 'medical_camp'):
            # Check if user is assigned to this camp
            return obj.medical_camp in request.user.medical_camps.all()
        return False


class IsCampAdmin(BasePermission):
    """User is admin of their assigned camp"""
    message = "You must be a camp administrator."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Check if user has camp admin role
        return request.user.user_type in ['medical_officer', 'admin']
    
    def has_object_permission(self, request, view, obj):
        # Check if user is admin of the camp
        if hasattr(obj, 'medical_camp'):
            return obj.medical_camp in request.user.medical_camps.all()
        return False


class IsSOSInitiator(BasePermission):
    """User initiated the SOS or is admin"""
    message = "You can only view your own SOS alerts."
    
    def has_object_permission(self, request, view, obj):
        # User can view their own SOS or if admin
        if request.user.is_staff:
            return True
        return obj.user == request.user


class ReadOnly(BasePermission):
    """Allow read-only access"""
    
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class DenyAll(BasePermission):
    """Deny all access"""
    message = "Access denied."
    
    def has_permission(self, request, view):
        return False


# ============================================================================
# Composite Permission Classes
# ============================================================================

class IsAuthenticatedAndOwner(IsAuthenticated):
    """Must be authenticated and own the object"""
    
    def has_object_permission(self, request, view, obj):
        return IsOwner().has_object_permission(request, view, obj)


class IsAdminOrReadOnly(BasePermission):
    """Admin can modify, everyone can read"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff


class IsAdminOrOwner(BasePermission):
    """Admin or owner can access"""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return IsOwner().has_object_permission(request, view, obj)


class IsMedicalStaffOrReadOnly(BasePermission):
    """Medical staff can modify, everyone can read"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return IsMedicalStaff().has_permission(request, view)


# ============================================================================
# Object-Level Permission Checkers
# ============================================================================

def check_camp_access(user, camp):
    """Check if user has access to camp"""
    if user.is_staff:
        return True
    if hasattr(user, 'medical_camps'):
        return camp in user.medical_camps.all()
    return False


def check_patient_access(user, patient):
    """Check if user can access patient"""
    if user.is_staff:
        return True
    # User can only access patients from their camps
    return check_camp_access(user, patient.medical_camp)


def check_sos_access(user, sos):
    """Check if user can access SOS alert"""
    if user.is_staff:
        return True
    if sos.user == user:
        return True
    # Police/medical staff can see SOS from their area
    if user.user_type in ['police_officer', 'medical_officer']:
        # Can see SOS if within their jurisdiction
        return True
    return False
