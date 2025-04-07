from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    def create_user(self, email, role, password, is_staff=False, is_superuser=False):
        if not email:
            raise ValidationError("Email обязателен")
        if not password:
            raise ValidationError("Password обязателен")
        if role == "admin":
            raise ValidationError("Нельзя создать админа этим путем")

        user = self.model(email=self.normalize_email(email), role=role, is_staff=is_staff, is_superuser=is_superuser)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("role") != "admin":
            raise ValidationError("Superuser должен иметь role=admin")

        if not extra_fields.get("is_staff"):
            raise ValidationError("Superuser должен иметь is_staff=True")

        if not extra_fields.get("is_superuser"):
            raise ValidationError("Superuser должен иметь is_superuser=True")

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
    is_superuser = models.BooleanField(default=False)

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

    LAW_CHOICES = [
        ('44_FZ', '44-ФЗ'),
        ('223_FZ', '223-ФЗ'),
    ]

    DELIVERY_REGION_CHOICES = [
        ("Алтайский край", "Алтайский край"),
        ("Амурская область", "Амурская область"),
        ("Архангельская область", "Архангельская область"),
        ("Астраханская область", "Астраханская область"),
        ("Байконур", "Байконур"),
        ("Белгородская область", "Белгородская область"),
        ("Брянская область", "Брянская область"),
        ("Владимирская область", "Владимирская область"),
        ("Волгоградская область", "Волгоградская область"),
        ("Вологодская область", "Вологодская область"),
        ("Воронежская область", "Воронежская область"),
        ("Донецкая Народная Республика", "Донецкая Народная Республика"),
        ("Еврейская автономная область", "Еврейская автономная область"),
        ("Забайкальский край", "Забайкальский край"),
        ("Запорожская область", "Запорожская область"),
        ("Ивановская область", "Ивановская область"),
        ("Иркутская область", "Иркутская область"),
        ("Кабардино-Балкарская Республика", "Кабардино-Балкарская Республика"),
        ("Калининградская область", "Калининградская область"),
        ("Калужская область", "Калужская область"),
        ("Камчатский край", "Камчатский край"),
        ("Карачаево-Черкесская Республика", "Карачаево-Черкесская Республика"),
        ("Кемеровская область - Кузбасс", "Кемеровская область - Кузбасс"),
        ("Кировская область", "Кировская область"),
        ("Костромская область", "Костромская область"),
        ("Краснодарский край", "Краснодарский край"),
        ("Красноярский край", "Красноярский край"),
        ("Курганская область", "Курганская область"),
        ("Курская область", "Курская область"),
        ("Ленинградская область", "Ленинградская область"),
        ("Липецкая область", "Липецкая область"),
        ("Луганская Народная Республика", "Луганская Народная Республика"),
        ("Магаданская область", "Магаданская область"),
        ("Москва", "Москва"),
        ("Московская область", "Московская область"),
        ("Мурманская область", "Мурманская область"),
        ("Ненецкий автономный округ (Архангельская область)", "Ненецкий автономный округ (Архангельская область)"),
        ("Нижегородская область", "Нижегородская область"),
        ("Новгородская область", "Новгородская область"),
        ("Новосибирская область", "Новосибирская область"),
        ("Омская область", "Омская область"),
        ("Оренбургская область", "Оренбургская область"),
        ("Орловская область", "Орловская область"),
        ("Пензенская область", "Пензенская область"),
        ("Пермский край", "Пермский край"),
        ("Приморский край", "Приморский край"),
        ("Псковская область", "Псковская область"),
        ("Республика Адыгея (Адыгея)", "Республика Адыгея (Адыгея)"),
        ("Республика Алтай", "Республика Алтай"),
        ("Республика Башкортостан", "Республика Башкортостан"),
        ("Республика Бурятия", "Республика Бурятия"),
        ("Республика Дагестан", "Республика Дагестан"),
        ("Республика Ингушетия", "Республика Ингушетия"),
        ("Республика Калмыкия", "Республика Калмыкия"),
        ("Республика Карелия", "Республика Карелия"),
        ("Республика Коми", "Республика Коми"),
        ("Республика Крым", "Республика Крым"),
        ("Республика Марий Эл", "Республика Марий Эл"),
        ("Республика Мордовия", "Республика Мордовия"),
        ("Республика Саха (Якутия)", "Республика Саха (Якутия)"),
        ("Республика Северная Осетия-Алания", "Республика Северная Осетия-Алания"),
        ("Республика Татарстан (Татарстан)", "Республика Татарстан (Татарстан)"),
        ("Республика Тыва", "Республика Тыва"),
        ("Республика Хакасия", "Республика Хакасия"),
        ("Ростовская область", "Ростовская область"),
        ("Рязанская область", "Рязанская область"),
        ("Самарская область", "Самарская область"),
        ("Санкт-Петербург", "Санкт-Петербург"),
        ("Саратовская область", "Саратовская область"),
        ("Сахалинская область", "Сахалинская область"),
        ("Свердловская область", "Свердловская область"),
        ("Севастополь", "Севастополь"),
        ("Смоленская область", "Смоленская область"),
        ("Ставропольский край", "Ставропольский край"),
        ("Тамбовская область", "Тамбовская область"),
        ("Тверская область", "Тверская область"),
        ("Томская область", "Томская область"),
        ("Тульская область", "Тульская область"),
        ("Тюменская область", "Тюменская область"),
        ("Удмуртская Республика", "Удмуртская Республика"),
        ("Ульяновская область", "Ульяновская область"),
        ("Хабаровский край", "Хабаровский край"),
        ("Ханты-Мансийский автономный округ - Югра (Тюменская область)", "Ханты-Мансийский автономный округ - Югра (Тюменская область)"),
        ("Херсонская область", "Херсонская область"),
        ("Челябинская область", "Челябинская область"),
        ("Чеченская Республика", "Чеченская Республика"),
        ("Чувашская Республика - Чувашия", "Чувашская Республика - Чувашия"),
        ("Чукотский автономный округ", "Чукотский автономный округ"),
        ("Ямало-Ненецкий автономный округ (Тюменская область)", "Ямало-Ненецкий автономный округ (Тюменская область)"),
        ("Ярославская область", "Ярославская область"),
    ]

    okpd2 = models.CharField(max_length=5, choices=OKPD2_CHOICES, verbose_name="Сфера деятельности по ОКПД2")
    description = models.TextField(verbose_name="Описание заказа")
    contract_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма контракта")
    delivery_region = models.CharField(max_length=255, choices=DELIVERY_REGION_CHOICES, verbose_name="Регион поставки")

    law_type = models.CharField(max_length=6, choices=LAW_CHOICES, default='44_FZ', verbose_name="Закон, по которому организуется заказ")

    def __str__(self):
        return f"Заказ от {self.customer.name or self.customer.email} ({self.law_type})"
    


class Supplier(models.Model):

    OKFS_CHOICES = [
        ("Частная собственность", "Частная собственность"),
        ("Государственная собственность", "Государственная собственность"),
        ("Индивидуальные предприниматели", "Индивидуальные предприниматели"),
        ("Собственность иностранных граждан и лиц без гражданства", "Собственность иностранных граждан и лиц без гражданства"),
        ("Иная смешанная российская собственность", "Иная смешанная российская собственность"),
        ("Совместная частная и иностранная собственность", "Совместная частная и иностранная собственность"),
        ("Федеральная собственность", "Федеральная собственность")
    ]

    OKOPF_CHOICES = [
        ("Общества с ограниченной ответственностью", "Общества с ограниченной ответственностью"),
        ("Акционерные общества", "Акционерные общества"),
        ("Индивидуальные предприниматели", "Индивидуальные предприниматели"),
        ("Закрытые акционерные общества", "Закрытые акционерные общества"),
        ("Открытые акционерные общества", "Открытые акционерные общества"),
        ("Казенные учреждения", "Казенные учреждения")
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='supplier_profile',
        verbose_name="Пользователь"
    )

    full_name = models.TextField(verbose_name="Полное наименование")
    short_name = models.TextField(blank=True, null=True, verbose_name="Сокращенное наименование")
    short_name_english = models.TextField(blank=True, null=True, verbose_name="Сокращенное наименование на английском")

    judicial_address = models.TextField(blank=True, null=True, verbose_name="Юридический адрес")

    email = models.EmailField(
        blank=True, 
        null=True, 
        validators=[EmailValidator(message="Введите корректный email адрес")],
        verbose_name="Email"
    )
    leader = models.TextField(blank=True, null=True, verbose_name="Руководитель")


    registration_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата регистрации")


    okved = models.CharField(max_length=10, blank=True, null=True, verbose_name="ОКВЭД")
    index_due_diligence = models.IntegerField(blank=True, null=True, verbose_name="Индекс должной осмотрительности")

    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")

    kpp = models.CharField(max_length=9, blank=True, null=True, verbose_name="КПП")

    ogrn = models.CharField(max_length=15, unique=True, verbose_name="ОГРН")
    okpo = models.CharField(max_length=12, unique=True, verbose_name="ОКПО")

    okfs = models.CharField(max_length=64, choices=OKFS_CHOICES, verbose_name="ОКФС")
    okopf = models.CharField(max_length=64, choices=OKOPF_CHOICES, verbose_name="ОКОПФ")

    @property
    def index_due_diligence_word(self):
        if self.index_due_diligence is None:
            return None
        if 1 <= self.index_due_diligence <= 40:
            return "Низкий риск"
        elif 41 <= self.index_due_diligence <= 70:
            return "Средний риск"
        elif 71 <= self.index_due_diligence <= 99:
            return "Высокий риск"
        return None

    def clean(self):
        super().clean()
        if self.email and not self.user.email:
            self.user.email = self.email
            self.user.save()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ['full_name']


class SupplierSubscription(models.Model):
    supplier = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': User.Role.SUPPLIER}, 
        verbose_name="Поставщик"
    )
    OKPD2_CHOICES = [
        ("29.10", "29.10"),
        ("29.20", "29.20"),
        ("29.31", "29.31"),
        ("29.32", "29.32"),
    ]
    okpd2 = models.CharField(max_length=5, choices=OKPD2_CHOICES, verbose_name="Код ОКПД2")

    class Meta:
        unique_together = ('supplier', 'okpd2')

    def __str__(self):
        return f"{self.supplier.email} -> {self.okpd2}"


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время запроса")
    request_data = models.JSONField(verbose_name="Параметры запроса")
    recommended_suppliers = models.JSONField(verbose_name="Рекомендованные поставщики")
    top_only = models.BooleanField(default=False, verbose_name="Параметр")

    class Meta:
        ordering = ["-timestamp"]
