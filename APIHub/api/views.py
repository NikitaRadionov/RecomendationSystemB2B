from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import *

from .serializers import OrderSerializer, SupplierSerializer
from .models import Supplier, Order
from .permissions import IsSupplierPermission, IsCustomerPermission, IsCustomerReadOnlyPermission, IsAdminPermission

class ListCreateOrderAPIView(ListCreateAPIView):
    permission_classes = [IsCustomerPermission|IsAdminPermission]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['law_type']
    ordering_fields = ['contract_amount']
    search_fields = ['description']

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


list_create_order_view = ListCreateOrderAPIView.as_view()

class RUDOrderAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCustomerPermission|IsAdminPermission]
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

rud_order_view = RUDOrderAPIView.as_view()


class ListCreateSupplierAPIView(ListCreateAPIView):
    queryset = Supplier.objects.all()
    permission_classes = [IsCustomerReadOnlyPermission|IsSupplierPermission|IsAdminPermission]
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['full_name', 'short_name', 'judicial_address', 
                        'registration_date', 'okved', 'inn', 'ogrn', 'index_due_diligence']
    
    search_fields = ['full_name', 'short_name', 'judicial_address', 'email']
    
    ordering_fields = ['registration_date', 'index_due_diligence', 'full_name']


list_create_supplier_view = ListCreateSupplierAPIView.as_view()

class RUDSupplierAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    permission_classes = [IsSupplierPermission|IsAdminPermission]
    serializer_class = SupplierSerializer
    lookup_field = "inn"



rud_supplier_view = RUDSupplierAPIView.as_view()
