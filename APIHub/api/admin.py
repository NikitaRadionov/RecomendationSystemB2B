from django.contrib import admin
from .models import User, Order, Supplier, SupplierSubscription, RecommendationHistory

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

@admin.register(SupplierSubscription)
class SupplierSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("supplier", "okpd2")  # Какие поля отображать в списке
    search_fields = ("supplier__email", "okpd2")  # Поиск по email поставщика и коду ОКПД2
    list_filter = ("okpd2",)  # Фильтр по ОКПД2

@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "top_only")  # Отображаемые колонки
    search_fields = ("user__email",)  # Поиск по email пользователя
    list_filter = ("top_only", "timestamp")  # Фильтрация по флагу top_only и дате
    readonly_fields = ("timestamp", "request_data", "recommended_suppliers")  # Чтобы нельзя было редактировать

