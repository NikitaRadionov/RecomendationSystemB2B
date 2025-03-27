from django.contrib import admin
from .models import User, Order, Supplier

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "role", "is_active", "is_staff")
    search_fields = ("email", "name")
    list_filter = ("role", "is_active", "is_staff")
    ordering = ("email",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("customer", "okpd2", "contract_amount", "delivery_region", "law_type")
    search_fields = ("customer__email", "description", "delivery_region")
    list_filter = ("okpd2", "law_type")

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "inn", "ogrn")
    search_fields = ("full_name", "email", "inn", "ogrn")
    list_filter = ("okved", "index_due_diligence_word")