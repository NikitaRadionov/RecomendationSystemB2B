from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission


class UserManager(BaseUserManager):
    def create_user(self, email, role, password, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        if role == "admin":
            raise ValueError("Cannot create an admin user this way")

        user = self.model(email=self.normalize_email(email), role=role, is_staff=is_staff, is_superuser=is_superuser)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("role") != "admin":
            raise ValueError("Superuser must have role=admin")

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")

        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMINISTRATOR = "admin", 'Administrator'
        CUSTOMER = "customer", 'Customer'
        SUPPLIER = "supplier", 'Supplier'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group, 
        related_name="user_groups",
        blank=True, 
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="user_permissions",
        blank=True, 
        help_text="Specific permissions for this user."
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.email


class Order(models.Model):
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name="Заказчик"
    )
    OKPD2_CHOICES = [
        ("29.10", "29.10"),
        ("29.20", "29.20"),
        ("29.31", "29.31"),
        ("29.32", "29.32"),
    ]

    okpd2 = models.CharField(
        max_length=5,
        choices=OKPD2_CHOICES,
        verbose_name="Сфера деятельности по ОКПД2"
    )
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
        return f"Заказ от {self.customer.name or self.customer.email} ({self.law_type})"
    


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


class SupplierSubscription(models.Model):
    supplier = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': User.Role.SUPPLIER}, 
        verbose_name="Поставщик"
    )
    okpd2 = models.CharField(max_length=10, verbose_name="Код ОКПД2")

    class Meta:
        unique_together = ('supplier', 'okpd2')

    def __str__(self):
        return f"{self.supplier.email} -> {self.okpd2}"


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_data = models.JSONField()
    recommended_suppliers = models.JSONField()
    top_only = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
