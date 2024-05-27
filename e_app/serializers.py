from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Order, OrderItem, Cart, CartItem

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'quantity', 'retailer')

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'total_amount', 'created_at', 'order_items')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'total_amount', 'created_at')

class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'cart_items')

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product', 'quantity')
