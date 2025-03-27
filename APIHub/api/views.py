import logging
from django_filters.rest_framework import DjangoFilterBackend
from django.apps import apps
from django.db.models import F

from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.generics import *

from .serializers import OrderSerializer, SupplierSerializer, SupplierSubscriptionSerializer, RecommendationHistorySerializer
from .models import Supplier, Order, SupplierSubscription, User, RecommendationHistory
from .permissions import IsSupplierPermission, IsCustomerPermission, IsCustomerReadOnlyPermission, IsAdminPermission

from .utils import send_order_notifications

logger = logging.getLogger(__name__)

class ListCreateOrderAPIView(ListCreateAPIView):
    permission_classes = [IsCustomerPermission | IsAdminPermission]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["law_type"]
    ordering_fields = ["contract_amount"]
    search_fields = ["description"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        try:
            order = serializer.save(customer=self.request.user)
            logger.info(f"Создан заказ ID {order.id} пользователем {self.request.user}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении заказа: {str(e)}", exc_info=True)
            raise 

        order_details = {
            "description": order.description,
            "law_type": order.law_type,
            "contract_amount": order.contract_amount,
            "okpd2": order.okpd2,
            "delivery_region": order.delivery_region,
        }

        try:
            send_order_notifications(order_details)
            logger.info(f"Уведомления успешно отправлены для заказа ID {order.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомлений для заказа ID {order.id}: {str(e)}", exc_info=True)

list_create_order_view = ListCreateOrderAPIView.as_view()

class RUDOrderAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCustomerPermission | IsAdminPermission]
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)
    
    def perform_update(self, serializer):
        try:
            order = serializer.save()
            logger.info(f"Обновлен заказ ID {order.id} пользователем {self.request.user}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении заказа ID {self.get_object().id}: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            logger.info(f"Удален заказ ID {instance.id} пользователем {self.request.user}")
            instance.delete()
        except Exception as e:
            logger.error(f"Ошибка при удалении заказа ID {instance.id}: {str(e)}")
            raise

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

    def perform_create(self, serializer):
        try:
            supplier = serializer.save()
            logger.info(f"Поставщик {supplier.inn} создан пользователем {self.request.user.email}")
        except Exception as e:
            logger.error(f"Ошибка при создании поставщика: {str(e)}")
            raise


list_create_supplier_view = ListCreateSupplierAPIView.as_view()

class RUDSupplierAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    permission_classes = [IsSupplierPermission|IsAdminPermission]
    serializer_class = SupplierSerializer
    lookup_field = "inn"

    def perform_update(self, serializer):
        try:
            supplier = serializer.save()
            logger.info(f"Поставщик {supplier.inn} обновлен пользователем {self.request.user.email}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении поставщика {self.get_object().inn}: {str(e)}")
            raise

    def perform_destroy(self, instance):
        try:
            logger.info(f"Поставщик {instance.inn} удален пользователем {self.request.user.email}")
            instance.delete()
        except Exception as e:
            logger.error(f"Ошибка при удалении поставщика {instance.inn}: {str(e)}")
            raise


rud_supplier_view = RUDSupplierAPIView.as_view()


class SupplierRecommendationView(APIView):

    permission_classes = [IsCustomerPermission|IsAdminPermission]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ml_model = apps.get_app_config('api').ml_model

    def post(self, request):
        data = request.data
        logger.info(f"Запрос на рекомендации от пользователя {request.user}, данные: {data}")
        top_only = bool(int(request.query_params.get("top_only", "0")))

        required_fields = {"okpd2", "description", "contract_amount", "delivery_region", "law_type"}

        if not required_fields.issubset(data.keys()):
            logger.warning(f"Недостаточно данных для предсказания: {data}")
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            predictions = self.ml_model.predict(data)
            if not predictions:
                logger.warning("Модель не смогла сделать предсказание")
                return Response(status=status.HTTP_204_NO_CONTENT)
            

            suppliers = Supplier.objects.filter(inn__in=predictions)

            if top_only:
                suppliers = suppliers[:1]            
            
            serializer = SupplierSerializer(suppliers, many=True)

            RecommendationHistory.objects.create(
                user=request.user,
                request_data=data,
                recommended_suppliers=[s.inn for s in suppliers],
                top_only=top_only
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Ошибка при предсказании: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


recomendation_view = SupplierRecommendationView.as_view()



class SupplierSubscriptionListCreateView(ListCreateAPIView):
    serializer_class = SupplierSubscriptionSerializer
    permission_classes = [IsSupplierPermission|IsAdminPermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SupplierSubscription.objects.all()
        return SupplierSubscription.objects.filter(supplier=self.request.user)

    def perform_create(self, serializer):
        try:
            if self.request.user.is_staff:
                supplier_id = self.request.data.get("supplier_id")
                if supplier_id:
                    supplier = User.objects.filter(id=supplier_id, role="supplier").first()
                    if supplier:
                        logger.info(f"Администратор {self.request.user} добавил подписку для поставщика ID {supplier_id}")
                        serializer.save(supplier=supplier)
                        return
            logger.info(f"Поставщик {self.request.user} создал подписку")
            serializer.save(supplier=self.request.user)
        except Exception as e:
            logger.error(f"Ошибка при создании подписки: {str(e)}", exc_info=True)
            raise

list_create_subscription_view = SupplierSubscriptionListCreateView.as_view()


class SupplierSubscriptionDeleteView(DestroyAPIView):
    serializer_class = SupplierSubscriptionSerializer
    permission_classes = [IsSupplierPermission|IsAdminPermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SupplierSubscription.objects.all()
        return SupplierSubscription.objects.filter(supplier=self.request.user)

    def perform_destroy(self, instance):
        try:
            logger.info(f"Поставщик {self.request.user} удаляет подписку ID {instance.id}")
            instance.delete()
            logger.info(f"Подписка ID {instance.id} успешно удалена")
        except Exception as e:
            logger.error(f"Ошибка при удалении подписки ID {instance.id}: {str(e)}", exc_info=True)
            raise

destroy_subscription_view = SupplierSubscriptionDeleteView.as_view()


class CompareSuppliersView(APIView):
    permission_classes = [IsCustomerPermission | IsAdminPermission]

    def get(self, request):
        supplier_inns = request.query_params.getlist("inn")
        if not supplier_inns:
            return Response({"error": "INN поставщиков не переданы"}, status=status.HTTP_400_BAD_REQUEST)

        compare_by = request.query_params.getlist("compare_by", ["index_due_diligence", "registration_date"])

        if not supplier_inns:
            return Response({"error": "Поставщики с такими INN не найдены"}, status=status.HTTP_404_NOT_FOUND)

        suppliers = Supplier.objects.filter(inn__in=supplier_inns)

        if not suppliers:
            return Response({"error": "Поставщики с такими INN не найдены"}, status=status.HTTP_404_NOT_FOUND)

        comparison_results = []
        for supplier in suppliers:
            comparison_data = {
                "inn": supplier.inn,
                "full_name": supplier.full_name,
                "registration_date": supplier.registration_date,
                "index_due_diligence": supplier.index_due_diligence,
                "okved": supplier.okved
            }

            comparison_results.append(comparison_data)

        comparison_results = sorted(
            comparison_results,
            key=lambda x: tuple(F(field).desc() for field in compare_by),
            reverse=True
        )

        logger.info(f"Сравнение поставщиков по INN: {supplier_inns} с критериями: {compare_by}")
        
        return Response(comparison_results)

compare_suppliers_view = CompareSuppliersView.as_view()


class RecommendationHistoryView(ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsCustomerPermission|IsAdminPermission]

    def get_queryset(self):
        return RecommendationHistory.objects.filter(user=self.request.user)

history_view = RecommendationHistoryView.as_view()
