from django.core.mail import send_mail
from django.conf import settings
from .models import SupplierSubscription
import logging

logger = logging.getLogger(__name__)

def send_order_notifications(order_details):
    okpd2 = order_details.get('okpd2')
    
    if not okpd2:
        logger.error("Не указан ОКПД2 в деталях заказа")
        return
        
    subscribed_suppliers = SupplierSubscription.objects.filter(okpd2=okpd2).select_related('supplier', 'supplier__user')
    
    if not subscribed_suppliers.exists():
        logger.warning(f"Нет подписчиков на ОКПД2 {okpd2}")
        return
        
    recipient_list = []
    for subscription in subscribed_suppliers:
        supplier = subscription.supplier
        # Проверяем email в обеих моделях
        email = supplier.email or supplier.user.email
        if email:
            recipient_list.append(email)
            
    if not recipient_list:
        logger.warning(f"Нет email-адресов для отправки уведомлений по ОКПД2 {okpd2}")
        return

    try:
        send_mail(
            subject="Новый заказ, который может вас заинтересовать",
            message=(
                f"Описание: {order_details.get('description')}\n"
                f"Тип закона: {order_details.get('law_type')}\n"
                f"Сумма: {order_details.get('contract_amount')}\n"
                f"ОКПД2: {order_details.get('okpd2')}\n"
                f"Регион: {order_details.get('delivery_region')}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"Уведомления успешно отправлены для заказа с ОКПД2 {okpd2}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {str(e)}", exc_info=True)
