from django.urls import path
from .views import (
    LoginView, RegisterView, CurrentUserView,
    MaterialScanView, MaterialListView,
    ProductListView, ProductDetailView,
    InitiatePaymentView, VerifyPaymentView, ReleaseEscrowView,
    DeliveryTrackingView, ArtisanStatsView, MongoVaultView
)

urlpatterns = [
    # Auth & Security
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/me/', CurrentUserView.as_view(), name='api_me'),
    
    # AI Material Scanner
    path('materials/scan/', MaterialScanView.as_view(), name='api_material_scan'),
    path('materials/', MaterialListView.as_view(), name='api_material_list'),
    
    # Products & Smart Cataloging
    path('products/', ProductListView.as_view(), name='api_product_list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='api_product_detail'),
    
    # UPI Payments, Escrow & Orders
    path('payments/initiate/', InitiatePaymentView.as_view(), name='api_payment_initiate'),
    path('payments/verify/', VerifyPaymentView.as_view(), name='api_payment_verify'),
    path('orders/release-escrow/', ReleaseEscrowView.as_view(), name='api_release_escrow'),
    
    # Logistics & Delivery Partner Tracking
    path('delivery/track/<str:order_id>/', DeliveryTrackingView.as_view(), name='api_delivery_track'),
    
    # Artisan Metrics & MongoDB Store
    path('artisans/<uuid:pk>/stats/', ArtisanStatsView.as_view(), name='api_artisan_stats'),
    path('mongo/vault/', MongoVaultView.as_view(), name='api_mongo_vault'),
]
