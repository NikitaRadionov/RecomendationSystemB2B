from django.urls import path, include
from . import views

urlpatterns = [
    path('suppliers', views.list_create_supplier_view),
    path('suppliers/<str:inn>', views.rud_supplier_view),
    path('orders', views.list_create_order_view),
    path('orders/<int:pk>', views.rud_order_view),
    path('orders/<int:pk>/recommendation', views.order_recommendation_view),
    path('recommendation', views.recomendation_view),
    path('recommendation/history', views.history_view),
    path('subscriptions', views.list_create_subscription_view),
    path('subscriptions/<int:pk>', views.retrieve_destroy_subscription_view),
    path('compare-suppliers', views.compare_suppliers_view),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('drf-auth/', include('rest_framework.urls')),
]