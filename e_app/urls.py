from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from e_app.views import (UserRegistrationView, UserDetailView, ProductListView, ProductDetailView, ProductCreateView, ProductUpdateDeleteView, OrderListView, OrderCreateView, 
CartView,CartItemDeleteView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', ProductUpdateDeleteView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductUpdateDeleteView.as_view(), name='product_delete'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/<int:pk>/remove/',CartItemDeleteView.as_view(), name='cart-item-delete'),
]
