from rest_framework import serializers
from .models import User, Supplier, Order, SupplierSubscription, RecommendationHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        exclude = ["id"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['customer']


class SupplierSubscriptionSerializer(serializers.ModelSerializer):
    ALLOWED_OKPD2 = {"29.10", "29.20", "29.31", "29.32"}

    def validate_okpd2(self, value):
        if value not in self.ALLOWED_OKPD2:
            raise serializers.ValidationError("Недопустимый код ОКПД2.")
        return value
    
    class Meta:
        model = SupplierSubscription
        fields = ['id', 'okpd2']


class RecommendationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationHistory
        fields = "__all__"