from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Order, Supplier, User,  SupplierSubscription
from django.db import IntegrityError
from .utils import send_order_notifications


class OrderAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(email='customer@example.com', password='Av6ER2p9vB', role='customer')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='ofaqoOkJi7', role='admin')
        self.second_customer = User.objects.create_user(email='second.customer@example.com', password='YDjygmongb', role='customer')

        self.order = Order.objects.create(
            customer=self.customer,
            okpd2="29.10",
            description="Поставка автомобилей с бензиновым двигателем",
            contract_amount=5200000.00,
            delivery_region="Москва",
            law_type="44_FZ"
        )

    def test_customer_can_partial_update_own_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f'/api/orders/{self.order.pk}', data={'description': 'Обновленное описание'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Обновленное описание')

    def test_customer_can_update_own_order(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "okpd2": "29.31",
            "description": "Поставка автомобилей с бензиновым двигателем",
            "contract_amount": 7200000.00,
            "delivery_region": "Санкт-Петербург",
            "law_type": "223_FZ"
        }
        response = self.client.put(f'/api/orders/{self.order.pk}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_customer_can_delete_own_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/orders/{self.order.pk}', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_admin_can_partial_update_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/orders/{self.order.pk}', data={'description': 'Обновленное описание'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Обновленное описание')

    def test_admin_can_update_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/api/orders/{self.order.pk}', data={
            "okpd2": "29.20",
            "description": "Поставка автомобилей с бензиновым двигателем",
            "contract_amount": 2200000.00,
            "delivery_region": "Санкт-Петербург",
            "law_type": "223_FZ"
            }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_any_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/orders/{self.order.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_get_orders(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders')
        self.assertEqual(response.data['count'], 5)

    def test_admin_can_get_orders_sort(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders', {'ordering': 'contract_amount'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_orders_filter(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders', {'law_type': '44_FZ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_orders(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/orders/{self.order.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_customer_can_list_their_orders(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.order.pk)

        self.client.force_authenticate(user=self.second_customer)
        response = self.client.get('/api/orders')
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_other_user_cannot_modify_order(self):
        self.client.force_authenticate(user=self.second_customer)
        response = self.client.patch(f'/api/orders/{self.order.pk}', data={'description': 'Обновленное описание'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_create_order(self):
        response = self.client.post('/api/orders', {
            'law_type': '44_FZ',
            'okpd2': '29.32',
            'contract_amount': 2000000,
            'description': 'Автозапчасти для специализированных нужд',
            'delivery_region': 'Дагестан'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_order(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            'law_type': '223_FZ',
            'okpd2': '29.10',
            'contract_amount': 15000000,
            'description': 'Поставка легковых автомобилей',
            'delivery_region': 'Москва'
        }
        response = self.client.post('/api/orders', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def tearDown(self):
        Order.objects.all().delete()
        User.objects.all().delete()


class SupplierAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.supplier_user = User.objects.create_user(email='supplier@test.com', password='XmolKfcSbx', role='supplier')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='ofaqoOkJi7', role='admin')
        self.customer = User.objects.create_user(email='customer@example.com', password='Av6ER2p9vB', role='customer')

        self.supplier = Supplier.objects.create(
            user=self.supplier_user,
            full_name='ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЦЕНТРЗАПЧАСТЬ"',
            short_name='ООО "ЦЕНТРЗАПЧАСТЬ"',
            short_name_english='OOO "TSENTRZAPCHAST"',
            judicial_address='Белгородская обл, г.о. Старооскольский, г Старый Оскол, ул Чапаева, д. 37Б, помещ. 1',
            email='igor.kovalerenko@mail.ru',
            leader='Ковалеренко Игорь Владимирович',
            registration_date=None,
            okved='45.31',
            index_due_diligence=4,
            inn='3128121735',
            kpp='312801001',
            ogrn='1173123007354',
            okpo='06961674',
            okfs='Частная собственность',
            okopf='Общества с ограниченной ответственностью'
        )

    def test_customer_can_get_suppliers_filter(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/suppliers', {'index_due_diligence': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_get_suppliers_sort(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/suppliers', {'ordering': '-index_due_dilligence'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_supplier(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'user': self.supplier_user.id,
            "full_name": "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ \"БУДЕННОВСКИЙ КАМА-ЦЕНТР\"",
            "short_name": "ООО \"БУДЕННОВСКИЙ КАМА- ЦЕНТР\"",
            "short_name_english": "OOO \"BUDENNOVSKI KAMA- TSENTR\"",
            "judicial_address": "Город Буденновск, улица Комсомольская, д. 5",
            "email": "info@kama-centre.ru",
            "leader": "Иванов Иван Иванович",
            "registration_date": None,
            "okved": "45.21",
            "index_due_diligence": 5,
            "inn": "1234567891",
            "kpp": "123456789",
            "ogrn": "1234567890124",
            "okpo": "12345679",
            "okfs": "Государственная собственность",
            "okopf": "Открытые акционерные общества"
        }
        response = self.client.post('/api/suppliers', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_update_supplier(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'user': self.supplier_user.id,
            "full_name": "Обновленное full_name",
            "short_name": "Обновленный short_name",
            "short_name_english": "Обновленный short_name_english",
            "judicial_address": "Обновленный judicial_address",
            "email": "info_new_new@kama-centre.ru",
            "leader": "Иванов Иван Новый",
            "registration_date": None,
            "okved": "23.21",
            "index_due_diligence": 10,
            "inn": "1234567892",
            "kpp": "123456788",
            "ogrn": "1234567890123",
            "okpo": "12345675",
            "okfs": "Государственная собственность",
            "okopf": "Открытые акционерные общества"
        }
        response = self.client.put(f'/api/suppliers/{self.supplier.inn}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_partial_update_supplier(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "index_due_diligence": 8,
        }
        response = self.client.patch(f'/api/suppliers/{self.supplier.inn}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_supplier(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/suppliers/{self.supplier.inn}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_get_suppliers(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/suppliers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_suppliers_filter(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/suppliers', {'index_due_diligence': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_get_suppliers_sort(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/suppliers', {'ordering': '-index_due_dilligence'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_supplier_can_update(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {
            "full_name": "Обновленное full_name",
            "short_name": "Обновленный short_name",
            "short_name_english": "Обновленный short_name_english",
            "judicial_address": "Обновленный judicial_address",
            "email": "info_new_new@kama-centre.ru",
            "leader": "Иванов Иван Новый",
            "registration_date": None,
            "okved": "23.21",
            "index_due_diligence": 10,
            "inn": "1234567892",
            "kpp": "123456788",
            "ogrn": "1234567890123",
            "okpo": "12345675",
            "okfs": "Государственная собственность",
            "okopf": "Открытые акционерные общества"
        }
        response = self.client.patch(f'/api/suppliers/{self.supplier.inn}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_can_partial_update(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {
            'full_name': 'Обновленные данные'
        }
        response = self.client.patch(f'/api/suppliers/{self.supplier.inn}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Обновленные данные')

    def test_supplier_can_delete(self):
        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.delete(f'/api/suppliers/{self.supplier.inn}', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_list_suppliers_requires_auth(self):
        response = self.client.get('/api/suppliers')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def tearDown(self):
        Order.objects.all().delete()
        User.objects.all().delete()


class SupplierRecomendationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='test_customer@example.com', password='my_purpose_is_customer', role='customer')
        self.second_customer = User.objects.create_user(email='other@example.com', password='test', role='customer')
        self.customer_orders = [
            Order.objects.create(
                customer=self.customer,
                okpd2="29.10",
                description="Поставка легковых автомобилей с бензиновым двигателем",
                contract_amount=5200000.00,
                delivery_region="Москва",
                law_type="44_FZ"
            ),
            Order.objects.create(
                customer=self.customer,
                okpd2="29.20",
                description="Поставка кузовов для грузовиков",
                contract_amount=3100000.00,
                delivery_region="Санкт-Петербург",
                law_type="223_FZ"
            ),
            Order.objects.create(
                customer=self.customer,
                okpd2="29.31",
                description="Электрооборудование для авто",
                contract_amount=870000.00,
                delivery_region="Омская область",
                law_type="44_FZ"
            ),
            Order.objects.create(
                customer=self.customer,
                okpd2="29.32",
                description="Стеклоочистители для автобусов",
                contract_amount=450000.00,
                delivery_region="Пермский край",
                law_type="223_FZ"
            )
        ]
        self.second_customer_orders = [
            Order.objects.create(
                customer=self.second_customer,
                okpd2='29.10',
                description='Поставка автозапчастей для легковых автомобилей',
                contract_amount=1000000,
                delivery_region='Москва',
                law_type='44_FZ'
            )
        ]

    def test_recommendation_various_okpd(self):
        self.client.force_authenticate(user=self.customer)
        test_cases = [
            {
                'okpd2': '29.10',
                'description': 'Поставка легковых автомобилей с бензиновым двигателем',
                'contract_amount': 5200000.00,
                'delivery_region': 'Москва',
                'law_type': '44_FZ'
            },
            {
                'okpd2': '29.20',
                'description': 'Поставка кузовов для грузовиков',
                'contract_amount': 3100000.00,
                'delivery_region': 'Санкт-Петербург',
                'law_type': '223_FZ',
            },
            {
                'okpd2': '29.31',
                'description': 'Электрооборудование для авто',
                'contract_amount': 870000.00,
                'delivery_region': 'Омская область',
                'law_type': '44_FZ',
            },
            {
                'okpd2': '29.32',
                'description': 'Стеклоочистители для автобусов',
                'contract_amount': 450000.00,
                'delivery_region': 'Пермский край',
                'law_type': '223_FZ',
            },
        ]

        for case in test_cases:
            with self.subTest(okpd2=case["okpd2"]):
                response = self.client.post('/api/recommendation', data=case)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    msg=f"Ошибка при рекомендации для OKPD2: {case['okpd2']}"
                )

    def test_order_pk_recommendation_various_okpd(self):
        self.client.force_authenticate(user=self.customer)
        for order in self.customer_orders:
            with self.subTest(okpd2=order.okpd2):
                response = self.client.get(f'/api/orders/{order.pk}/recommendation')
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        Order.objects.all().delete()
        User.objects.all().delete()

class CompareSuppliersAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='test_customer@example.com', password='my_purpose_is_customer', role='customer')
        self.supplier_user = User.objects.create_user(email='supplier@test.com', password='XmolKfcSbx', role='supplier')
        self.supplier1 = Supplier.objects.create(
            user=self.supplier_user,
            full_name='ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЦЕНТРЗАПЧАСТЬ"',
            short_name='ООО "ЦЕНТРЗАПЧАСТЬ"',
            short_name_english='OOO "TSENTRZAPCHAST"',
            judicial_address='Белгородская обл, г.о. Старооскольский, г Старый Оскол, ул Чапаева, д. 37Б, помещ. 1',
            email='igor.kovalerenko@mail.ru',
            leader='Ковалеренко Игорь Владимирович',
            registration_date=None,
            okved='45.31',
            index_due_diligence=6,
            inn='3128121736',
            kpp='312801001',
            ogrn='1173123007350',
            okpo='06961672',
            okfs='Частная собственность',
            okopf='Общества с ограниченной ответственностью'
        )
        self.supplier2 = Supplier.objects.create(
            user=self.supplier_user,
            full_name='ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЦЕНТРЗАПЧАСТЬ"',
            short_name='ООО "ЦЕНТРЗАПЧАСТЬ"',
            short_name_english='OOO "TSENTRZAPCHAST"',
            judicial_address='Белгородская обл, г.о. Старооскольский, г Старый Оскол, ул Чапаева, д. 37Б, помещ. 1',
            email='igor.kovalerenko@mail.ru',
            leader='Ковалеренко Игорь Владимирович',
            registration_date=None,
            okved='45.31',
            index_due_diligence=4,
            inn='3128121735',
            kpp='312801001',
            ogrn='1173123007357',
            okpo='06961674',
            okfs='Частная собственность',
            okopf='Общества с ограниченной ответственностью'
        )
    
    def test_customer_can_comparesuppliers(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/api/compare-suppliers?inn={self.supplier1.inn}&inn={self.supplier2.inn}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def tearDown(self):
        Order.objects.all().delete()
        User.objects.all().delete()


class SupplierSubscriptionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email='admin@example.com', password='ofaqoOkJi7', role='admin')
        self.supplier_user = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            role='supplier'
        )
        self.subscription_data = {
            'supplier': self.supplier_user,
            'okpd2': '29.10'
        }
        self.subscription = SupplierSubscription.objects.create(supplier=self.supplier_user, okpd2='29.20')

    def test_admin_can_get_subscriptions(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/subscriptions')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_subscription(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "supplier_id": self.supplier_user.pk,
            "okpd2": "29.10"
        }
        response = self.client.post(f'/api/subscriptions', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_delete_subscription(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/subscriptions/{self.subscription.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_supplier_can_get_subscriptions(self):
        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.get(f'/api/subscriptions/{self.subscription.pk}', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_supplier_can_delete_subscription(self):
        self.client.force_authenticate(user=self.supplier_user)
        response = self.client.delete(f'/api/subscriptions/{self.subscription.pk}', format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_subscription(self):
        subscription = SupplierSubscription.objects.create(**self.subscription_data)
        self.assertEqual(subscription.supplier, self.supplier_user)
        self.assertEqual(subscription.okpd2, '29.10')