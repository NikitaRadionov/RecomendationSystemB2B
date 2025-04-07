from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order, Supplier, User
from django.core import mail
from django.test import override_settings


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

    def test_customer_can_update_own_order(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(f'/api/orders/{self.order.pk}', data={'description': 'Обновленное описание'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Обновленное описание')

    def test_customer_can_list_their_orders_only(self):
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

    def test_admin_can_delete_any_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/orders/{self.order.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_see_all_orders(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders')
        self.assertEqual(response.data['count'], Order.objects.count())


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
            registration_date='2017-03-06',
            okved='45.31',
            index_due_diligence=4,
            inn='3128121735',
            kpp='312801001',
            ogrn='1173123007354',
            okpo='06961674',
            okfs='Частная собственность',
            okopf='Общества с ограниченной ответственностью'
        )

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
            "registration_date": "2022-06-15",
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

    def test_admin_can_delete_supplier(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/suppliers/{self.supplier.inn}')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_supplier_can_update_self(self):
        self.client.force_authenticate(user=self.supplier_user)
        data = {
            'full_name': 'Обновленные данные'
        }
        response = self.client.patch(f'/api/suppliers/{self.supplier.inn}', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Обновленные данные')

    def test_list_suppliers_requires_auth(self):
        response = self.client.get('/api/suppliers')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_create_supplier(self):
        response = self.client.post('/api/suppliers', {
            "full_name": "Коваленко Дмитрий",
            "judicial_address": "г. Москва",
            "email": "supplier@domain.com",
            "leader": "Коваленко Игорь",
            "registration_date": "2020-02-01",
            "okved": "45.11",
            "index_due_diligence": 3,
            "inn": "3216549872",
            "kpp": "321654987",
            "ogrn": "9876543212346",
            "okpo": "98765433",
            "okfs": "Частная собственность",
            "okopf": "Общества с ограниченной ответственностью"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_supplier(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/suppliers/{self.supplier.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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


class ModelTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
        self.supplier = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            role='supplier'
        )

    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(
            email='new@example.com',
            password='testpass123',
            role='customer'
        )
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, 'customer')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'admin')

    def test_create_order(self):
        """Test creating a new order"""
        order = Order.objects.create(
            customer=self.customer,
            description='Test order',
            law_type='44_FZ',
            contract_amount=100000.00,
            okpd2='29.10',
            delivery_region='Москва'
        )
        self.assertEqual(str(order), f'Order {order.id}')
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.description, 'Test order')

    def test_create_supplier(self):
        """Test creating a new supplier"""
        supplier = Supplier.objects.create(
            user=self.supplier,
            full_name='Test Supplier',
            short_name='TS',
            inn='1234567890',
            ogrn='1234567890123',
            okpo='12345678',
            okved='29.10',
            judicial_address='Test Address'
        )
        self.assertEqual(str(supplier), 'Test Supplier')
        self.assertEqual(supplier.user, self.supplier)
        self.assertEqual(supplier.inn, '1234567890')


class SerializerTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
        self.supplier = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            role='supplier'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            description='Test order',
            law_type='44_FZ',
            contract_amount=100000.00,
            okpd2='29.10',
            delivery_region='Москва'
        )
        self.supplier_obj = Supplier.objects.create(
            user=self.supplier,
            full_name='Test Supplier',
            short_name='TS',
            inn='1234567890',
            ogrn='1234567890123',
            okpo='12345678',
            okved='29.10',
            judicial_address='Test Address'
        )

    def test_order_serializer(self):
        """Test order serializer"""
        from .serializers import OrderSerializer
        serializer = OrderSerializer(self.order)
        self.assertEqual(serializer.data['description'], 'Test order')
        self.assertEqual(serializer.data['law_type'], '44_FZ')
        self.assertEqual(float(serializer.data['contract_amount']), 100000.00)

    def test_supplier_serializer(self):
        """Test supplier serializer"""
        from .serializers import SupplierSerializer
        serializer = SupplierSerializer(self.supplier_obj)
        self.assertEqual(serializer.data['full_name'], 'Test Supplier')
        self.assertEqual(serializer.data['inn'], '1234567890')
        self.assertEqual(serializer.data['okved'], '29.10')


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
        self.supplier = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            role='supplier'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            description='Test order',
            law_type='44_FZ',
            contract_amount=100000.00,
            okpd2='29.10',
            delivery_region='Москва'
        )

    def test_customer_permissions(self):
        """Test customer permissions"""
        from .permissions import IsCustomerPermission
        permission = IsCustomerPermission()
        
        # Test with customer
        request = type('Request', (), {'user': self.customer})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Test with supplier
        request = type('Request', (), {'user': self.supplier})()
        self.assertFalse(permission.has_permission(request, None))
        
        # Test with admin
        request = type('Request', (), {'user': self.admin})()
        self.assertFalse(permission.has_permission(request, None))

    def test_supplier_permissions(self):
        """Test supplier permissions"""
        from .permissions import IsSupplierPermission
        permission = IsSupplierPermission()
        
        # Test with supplier
        request = type('Request', (), {'user': self.supplier})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Test with customer
        request = type('Request', (), {'user': self.customer})()
        self.assertFalse(permission.has_permission(request, None))
        
        # Test with admin
        request = type('Request', (), {'user': self.admin})()
        self.assertFalse(permission.has_permission(request, None))

    def test_admin_permissions(self):
        """Test admin permissions"""
        from .permissions import IsAdminPermission
        permission = IsAdminPermission()
        
        # Test with admin
        request = type('Request', (), {'user': self.admin})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Test with customer
        request = type('Request', (), {'user': self.customer})()
        self.assertFalse(permission.has_permission(request, None))
        
        # Test with supplier
        request = type('Request', (), {'user': self.supplier})()
        self.assertFalse(permission.has_permission(request, None))


class EmailTests(TestCase):
    def setUp(self):
        self.supplier = User.objects.create_user(
            email='supplier@example.com',
            password='testpass123',
            role='supplier'
        )
        self.supplier_obj = Supplier.objects.create(
            user=self.supplier,
            full_name='Test Supplier',
            short_name='TS',
            inn='1234567890',
            ogrn='1234567890123',
            okpo='12345678',
            okved='29.10',
            judicial_address='Test Address',
            email='supplier@example.com'
        )
        self.subscription = SupplierSubscription.objects.create(
            supplier=self.supplier,
            okpd2='29.10'
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_order_notification(self):
        from .utils import send_order_notifications
        
        order_details = {
            'description': 'Test order',
            'law_type': '44_FZ',
            'contract_amount': 100000.00,
            'okpd2': '29.10',
            'delivery_region': 'Москва'
        }
        
        send_order_notifications(order_details)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Новый заказ, который может вас заинтересовать")
        self.assertEqual(mail.outbox[0].to, ['supplier@example.com'])
        self.assertIn('Test order', mail.outbox[0].body)
        self.assertIn('44_FZ', mail.outbox[0].body)
        self.assertIn('100000.00', mail.outbox[0].body)
        self.assertIn('29.10', mail.outbox[0].body)
        self.assertIn('Москва', mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_order_notification_no_subscribers(self):
        from .utils import send_order_notifications
        
        order_details = {
            'description': 'Test order',
            'law_type': '44_FZ',
            'contract_amount': 100000.00,
            'okpd2': '29.20',  # Нет подписчиков на этот ОКПД2
            'delivery_region': 'Москва'
        }
        
        send_order_notifications(order_details)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_order_notification_no_email(self):
        from .utils import send_order_notifications
        
        # Удаляем email у поставщика
        self.supplier_obj.email = None
        self.supplier_obj.save()
        
        order_details = {
            'description': 'Test order',
            'law_type': '44_FZ',
            'contract_amount': 100000.00,
            'okpd2': '29.10',
            'delivery_region': 'Москва'
        }
        
        send_order_notifications(order_details)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_order_notification_missing_okpd2(self):
        from .utils import send_order_notifications
        
        order_details = {
            'description': 'Test order',
            'law_type': '44_FZ',
            'contract_amount': 100000.00,
            'delivery_region': 'Москва'
            # Отсутствует okpd2
        }
        
        send_order_notifications(order_details)
        self.assertEqual(len(mail.outbox), 0)