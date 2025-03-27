from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsCustomerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "customer"


class IsCustomerReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        allowed = (
            request.method in SAFE_METHODS and 
            request.user.is_authenticated and 
            request.user.role == "customer"
        )
        return allowed


class IsSupplierPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "supplier"