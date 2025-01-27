from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, role, password):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        return self.create_user(email, role="admin", password=password)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMINISTRATOR = "admin", 'Administrator'
        CUSTOMER = "customer", 'Customer'
        SUPPLIER = "supplier", 'Supplier'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    is_active = models.BooleanField(default=True)       # Активный ли пользователь. Для того, чтобы можно было выдавать заморозку пользователю.
    is_staff = models.BooleanField(default=False)       # Разрешение на вход в административную панель django

    groups = models.ManyToManyField(
        Group, 
        related_name="user_groups",  # Уникальное имя для связи с группами
        blank=True, 
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="user_permissions",  # Уникальное имя для связи с разрешениями
        blank=True, 
        help_text="Specific permissions for this user."
    )

    objects = UserManager()

    USERNAME_FIELD = "email"                    # Идентификатор для аутентификации
    REQUIRED_FIELDS = ["role"]                  # Список дополнительных полей, которые необходимо указывать при создании суперпользователя

    def __str__(self):
        return self.email


class Order(models.Model):
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name="Заказчик"
    )
    okpd2 = models.CharField(max_length=255, verbose_name="Сфера деятельности по ОКПД2")
    description = models.TextField(verbose_name="Описание заказа")
    contract_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма контракта")
    delivery_region = models.CharField(max_length=255, verbose_name="Регион поставки")

    LAW_CHOICES = [
        ('44_FZ', '44-ФЗ'),
        ('223_FZ', '223-ФЗ'),
    ]
    law_type = models.CharField(
        max_length=6, 
        choices=LAW_CHOICES, 
        default='44_FZ', 
        verbose_name="Закон, по которому организуется заказ"
    )

    def __str__(self):
        return f"Заказ от {self.customer_name} ({self.law_type})"    


class Supplier(models.Model):
    full_name = models.TextField(blank=True, null=True)
    short_name = models.TextField(blank=True, null=True)
    short_name_english = models.TextField(blank=True, null=True)
    judicial_address = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    leader = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(blank=True, null=True)
    okved = models.CharField(max_length=10, blank=True, null=True)
    index_due_diligence = models.IntegerField(blank=True, null=True)
    index_due_diligence_word = models.TextField(blank=True, null=True)
    inn = models.CharField(max_length=12, blank=True, null=True, unique=True)
    kpp = models.CharField(max_length=9, blank=True, null=True)
    ogrn = models.CharField(max_length=15, blank=True, null=True, unique=True)
    okpo = models.CharField(max_length=12, blank=True, null=True)
    okfs = models.TextField(blank=True, null=True)
    okopf = models.TextField(blank=True, null=True)