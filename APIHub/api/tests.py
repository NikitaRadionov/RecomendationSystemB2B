from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order, Supplier

User = get_user_model()

class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='test_customer@customer.com', password='my_purpose_is_customer', role='customer')
        self.admin = User.objects.create_user(email='test_admin@admin.com', password='my_purpose_is_admin', role='admin')
        self.order = Order.objects.create(customer=self.customer, okpd2='29.32', law_type='44_FZ', contract_amount=1000000, description='BMW Engine', delivery_region='Дагестан')
        
    def test_list_orders_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_order_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        data = {'law_type': '44_FZ', 'okpd2': '29.32', 'contract_amount': 2000000, 'description': 'Mercedes Engine', 'delivery_region': 'Дагестан'}
        response = self.client.post('/api/orders', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f'/api/orders/{self.order.id}', {'description': 'Updated Mercedes Engine'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/orders/{self.order.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class SupplierAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.supplier = User.objects.create_user(email='test_supplier@supplier.com', password='my_purpose_is_passwrd', role='supplier')
        self.customer = User.objects.create_user(email='test_customer@customer.com', password='my_purpose_is_customer', role='customer')
        self.admin = User.objects.create_user(email='test_admin@admin.com', password='my_purpose_is_admin', role='admin')
        self.supplier_obj = Supplier.objects.create(full_name='Test Supplier', short_name='TS', judicial_address='123 Street', registration_date='2024-01-01', okved='1234', inn='1234567890', ogrn='0987654321', index_due_diligence=5)
    
    def test_list_suppliers(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/suppliers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_supplier(self):
        self.client.force_authenticate(user=self.admin)
        data = {'full_name': 'New Supplier', 'short_name': 'NS', 'judicial_address': '456 Road', 'registration_date': '2024-02-01', 'okved': '5678', 'inn': '2345678901', 'ogrn': '9876543210', 'index_due_diligence': 4}
        response = self.client.post('/api/suppliers', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        response = self.client.patch(f'/api/suppliers/{self.supplier_obj.inn}', {'full_name': 'Updated Supplier'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_supplier(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/suppliers/{self.supplier_obj.inn}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class SupplierRecomendationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='test_customer@customer.com', password='my_purpose_is_customer', role='customer')
    
    def test_supplier_recomendation(self):
        self.client.force_authenticate(user=self.customer)
        data = {'law_type': '44_FZ', 'okpd2': '29.32', 'contract_amount': 2000000, 'description': 'Mercedes Engine', 'delivery_region': 'Москва'}
        response = self.client.post('/api/recomendation', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
