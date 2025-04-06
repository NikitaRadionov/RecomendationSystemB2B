from rest_framework import serializers
from .models import User, Supplier, Order, SupplierSubscription, RecommendationHistory
from .validators import GarbageValueValidator
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.core.exceptions import ValidationError as DjangoValidationError

class UserSerializer(BaseUserCreateSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value
    
    def validate_role(self, value):
        if value == 'admin':
            raise serializers.ValidationError("Нельзя создать пользователя с ролью 'admin'")
        return value

    def create(self, validated_data):
        print('Я захожу сюда')
        try:
            return User.objects.create_user(**validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']


class SupplierSerializer(serializers.ModelSerializer):
    index_due_diligence_word = serializers.SerializerMethodField()
    full_name = serializers.CharField(
        validators=[GarbageValueValidator("Полное наименование", min_length=5, required=True)]
    )
    short_name = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        validators=[GarbageValueValidator("Краткое наименование")]
    )
    short_name_english = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        validators=[GarbageValueValidator("Краткое наименование (английский)", language="latin")]
    )
    judicial_address = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        validators=[GarbageValueValidator("Юридический адрес")]
    )

    leader = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        validators=[
            GarbageValueValidator("Руководитель", min_length=4, language="cyrillic")
        ]
    )

    class Meta:
        model = Supplier
        fields = "__all__"
    
    def get_index_due_diligence_word(self, obj):
        return obj.index_due_diligence_word
    
    def validate_inn(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("ИНН должен содержать только цифры.")
        if len(value) not in (10, 12):
            raise serializers.ValidationError("ИНН должен содержать 10 или 12 цифр.")
        return value

    def validate_kpp(self, value):
        if value is None:
            return value
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("КПП должен содержать только цифры.")
        if len(value) != 9:
            raise serializers.ValidationError("КПП должен содержать ровно 9 цифр.")
        return value

    def validate_ogrn(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("ОГРН должен содержать только цифры.")
        if len(value) not in (13, 15):
            raise serializers.ValidationError("ОГРН должен содержать 13 или 15 цифр.")
        return value

    def validate_okpo(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("ОКПО должен содержать только цифры.")
        if not (8 <= len(value) <= 12):
            raise serializers.ValidationError("ОКПО должен содержать от 8 до 12 цифр.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    description = serializers.CharField(
        validators=[GarbageValueValidator("Описание заказа", min_length=10, required=True)]
    )
    delivery_region = serializers.CharField(
        validators=[GarbageValueValidator("Регион поставки", min_length=3, required=True)]
    )

    class Meta:
        model = Order
        exclude = ['customer']

    def validate_contract_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма контракта не может быть отрицательным числом.")
        return value


class SupplierSubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SupplierSubscription
        fields = ['id', 'okpd2']
    
    def validate(self, attrs):
        request = self.context.get('request')
        okpd2 = attrs.get('okpd2')

        supplier = request.user
        if request.user.is_staff:
            supplier_id = request.data.get('supplier_id')
            if supplier_id:
                supplier = User.objects.filter(id=supplier_id, role="supplier").first()

        if supplier and SupplierSubscription.objects.filter(supplier=supplier, okpd2=okpd2).exists():
            raise serializers.ValidationError("Такая подписка уже существует.")

        return attrs


class RecommendationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationHistory
        fields = "__all__"