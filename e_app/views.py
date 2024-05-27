from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from .serializers import (UserSerializer,UserRegistrationSerializer,UserUpdateSerializer,ProductSerializer,ProductCreateUpdateSerializer,
    OrderSerializer,OrderCreateSerializer,CartSerializer,CartItemSerializer,)
from .decorators import role_required
from .models import Product, Order, Cart, CartItem, OrderItem
from allauth.account.views import ConfirmEmailView

User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(role_required('Retailer'))
    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(retailer=request.user)
            return Response({'message': 'Product created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(role_required('Retailer'))
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, retailer=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Product updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(role_required('Retailer'))
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, retailer=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'Customer':
            orders = Order.objects.filter(customer=request.user)
        else:
            orders = Order.objects.all()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(role_required('Customer'))
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(customer=request.user)
            send_order_confirmation_email(order, order.order_items.all())
            return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(role_required('Customer'))
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @method_decorator(role_required('Customer'))
    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart_item = serializer.save(cart=cart)
            return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(role_required('Customer'))
    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.filter(pk=pk, cart__user=request.user).first()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        if cart_item:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

def send_order_confirmation_email(order, order_items):
    subject = 'Order Confirmation'
    message = f'Thank you for your order!\n\nOrder ID: {order.id}\n\n'
    message += 'Items:\n'
    for item in order_items:
        message += f'{item.product.name} - {item.quantity} x ${item.product.price}\n'
    message += f'\nTotal: ${order.total_amount}'
    recipient_list = [order.customer.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

class ConfirmEmail(ConfirmEmailView):
    def get_template_names(self):
        return ['account/email_confirm.html']
