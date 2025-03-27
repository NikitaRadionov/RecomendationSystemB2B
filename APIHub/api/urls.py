from django.urls import path, include
from . import views

urlpatterns = [
    path('suppliers', views.list_create_supplier_view),
    path('suppliers/<int:inn>', views.rud_supplier_view),
    path('orders', views.list_create_order_view),
    path('orders/<int:id>', views.rud_order_view),
    path('recommendation', views.recomendation_view),
    path('recommendation/history', views.history_view),
    path('subscriptions', views.list_create_subscription_view),
    path('subscriptions/<int:pk>', views.destroy_subscription_view),
    path('compare-suppliers', views.compare_suppliers_view),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),  # /auth/jwt/create/, /auth/jwt/refresh/, /auth/jwt/verify/
    path('drf-auth/', include('rest_framework.urls')), # оставить только для тестирования
]