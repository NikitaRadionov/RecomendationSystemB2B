from django.urls import path, include
from .views import list_create_order_view, rud_order_view, list_create_supplier_view, rud_supplier_view

urlpatterns = [
    path('suppliers', list_create_supplier_view),
    path('suppliers/<int:inn>', rud_supplier_view),
    path('orders', list_create_order_view),
    path('orders/<int:id>', rud_order_view),
    # path('recomendation/<int:id>', recomendaiton_view)
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('drf-auth/', include('rest_framework.urls')),
]