from rest_framework import serializers
from .models import (
    UserProfile, ArtisanProfile, Material,
    MaterialScanLog, Product, DeliveryPartner, Order, EscrowTransaction
)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ArtisanProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    class Meta:
        model = ArtisanProfile
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class DeliveryPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartner
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    artisan_name = serializers.CharField(source='artisan.full_name', read_only=True)
    artisan_city = serializers.CharField(source='artisan.city', read_only=True)
    material_detail = MaterialSerializer(source='material', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class MaterialScanLogSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    assigned_delivery_partner = DeliveryPartnerSerializer(read_only=True)
    detected_properties = serializers.JSONField(source='get_detected_properties', read_only=True)

    class Meta:
        model = MaterialScanLog
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    delivery_partner_detail = DeliveryPartnerSerializer(source='delivery_partner', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class EscrowTransactionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    artisan_name = serializers.CharField(source='artisan.full_name', read_only=True)

    class Meta:
        model = EscrowTransaction
        fields = '__all__'
