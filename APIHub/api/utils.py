from django.core.mail import send_mail
from django.conf import settings
from .models import SupplierSubscription

def send_order_notifications(order_details):
    """
    Отправляет уведомления только подписанным поставщикам.
    """
    okpd2 = order_details.get('okpd2')

    subscribed_suppliers = SupplierSubscription.objects.filter(okpd2=okpd2).select_related('supplier')

    recipient_list = []
    for subscription in subscribed_suppliers:
        supplier = subscription.supplier
        if supplier.email:
            recipient_list.append(supplier.email)
            

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
