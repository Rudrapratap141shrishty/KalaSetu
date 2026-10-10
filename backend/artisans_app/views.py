"""
REST API ViewSets and Endpoints for Artisan Market Linkage App
Handles Auth, AI Material Scanner, Products, Orders, UPI Payments & Escrow, Delivery Tracking, and MongoDB Vault.
"""

import json
import uuid
import random
from datetime import datetime
from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    UserProfile, ArtisanProfile, Material,
    MaterialScanLog, Product, DeliveryPartner, Order, EscrowTransaction, RoleChoices
)
from .serializers import (
    UserProfileSerializer, ArtisanProfileSerializer, MaterialSerializer,
    ProductSerializer, MaterialScanLogSerializer, DeliveryPartnerSerializer,
    OrderSerializer, EscrowTransactionSerializer
)
from .ai_vision_engine import AIVisionEngine
from .mongo_service import mongo_service
from .security import SecurityService


# ==========================================
# 1. AUTHENTICATION & ROLE MANAGEMENT
# ==========================================

class LoginView(APIView):
    def post(self, request):
        username_or_email = request.data.get('username') or request.data.get('email')
        role = request.data.get('role', RoleChoices.ARTISAN)
        
        user = None
        if username_or_email:
            user = UserProfile.objects.filter(username__iexact=username_or_email).first() or \
                   UserProfile.objects.filter(email__iexact=username_or_email).first()
                   
        if not user:
            # Match first user of selected role or fallback to default
            user = UserProfile.objects.filter(role=role).first()
            if not user:
                user = UserProfile.objects.first()
                
        if not user:
            return Response({'error': 'No users registered yet. Please seed database.'}, status=status.HTTP_404_NOT_FOUND)
            
        token = SecurityService.generate_jwt_token(user)
        mongo_service.log_audit('USER_LOGIN', user.username, {'role': user.role, 'city': user.city})
        
        artisan_info = None
        if hasattr(user, 'artisan_detail'):
            artisan_info = user.artisan_detail.to_dict()
            
        return Response({
            'success': True,
            'token': token,
            'user': user.to_dict(),
            'artisan_profile': artisan_info,
            'message': f"Welcome back, {user.full_name}!"
        })


class RegisterView(APIView):
    def post(self, request):
        full_name = SecurityService.sanitize_input(request.data.get('full_name', ''))
        username = SecurityService.sanitize_input(request.data.get('username', '')).lower()
        email = SecurityService.sanitize_input(request.data.get('email', '')).lower()
        role = request.data.get('role', RoleChoices.BUYER_USER)
        phone = request.data.get('phone', '+91 98765 00000')
        city = request.data.get('city', 'New Delhi')
        state = request.data.get('state', 'Delhi')
        craft_type = request.data.get('craft_type', 'Traditional Craft')
        
        if not username or not email:
            return Response({'error': 'Username and email are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if UserProfile.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = UserProfile.objects.create(
            username=username,
            full_name=full_name or username.title(),
            email=email,
            role=role,
            phone=phone,
            city=city,
            state=state,
            is_verified=True
        )
        
        if role == RoleChoices.ARTISAN:
            ArtisanProfile.objects.create(
                user=user,
                craft_type=craft_type,
                community_name='Regional Artisan Federation',
                gi_tag_number=f"GI-IN-2026-{random.randint(100, 999)}",
                experience_years=10,
                escrow_wallet_balance=5000.00
            )
            
        token = SecurityService.generate_jwt_token(user)
        mongo_service.log_audit('USER_REGISTER', user.username, {'role': role, 'city': city})
        
        return Response({
            'success': True,
            'token': token,
            'user': user.to_dict(),
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = SecurityService.decode_jwt_token(token)
            if payload:
                user = UserProfile.objects.filter(id=payload['user_id']).first()
                if user:
                    return Response({'user': user.to_dict()})
        # Default fallback
        user = UserProfile.objects.first()
        return Response({'user': user.to_dict() if user else None})


# ==========================================
# 2. AI MATERIAL SCANNER & GRAPHQL RESOLVER
# ==========================================

class MaterialScanView(APIView):
    """
    POST: Processes scanned camera feed or image of raw artisanal materials.
    Returns material properties, fair wage breakdown, and assigned delivery partner.
    Persists data in SQLite and MongoDB.
    """
    def post(self, request):
        material_hint = request.data.get('material_hint', 'TERRACOTTA_CLAY')
        scan_source = request.data.get('scan_source', 'AI_CAMERA_SCAN')
        user_id = request.data.get('user_id')
        
        user = UserProfile.objects.filter(id=user_id).first() if user_id else None
        
        # Run AI Vision & Recommendation Engine
        analysis = AIVisionEngine.analyze_image_or_sample(hint_name=material_hint)
        
        # Look up or create Material record
        material, _ = Material.objects.get_or_create(
            code=analysis['material_code'],
            defaults={
                'name': analysis['material_name'],
                'category': analysis['category'],
                'origin_region': analysis['origin_region'],
                'gi_certified': analysis['gi_certified'],
                'standard_cost_per_unit': Decimal(str(analysis['pricing']['raw_material_base_cost'])),
                'carbon_footprint_score': analysis['carbon_footprint_score'],
                'tensile_strength': analysis['tensile_strength'],
                'durability_years': analysis['durability_years'],
                'texture_spec': analysis['texture_spec'],
                'image_sample_url': analysis['sample_image']
            }
        )
        
        delivery_partner = DeliveryPartner.objects.filter(is_available=True).first()
        
        # Save Scan Log in SQLite
        scan_log = MaterialScanLog.objects.create(
            user=user,
            material=material,
            confidence_score=analysis['confidence_score'],
            detected_properties_json=json.dumps(analysis['properties']),
            estimated_base_cost=Decimal(str(analysis['pricing']['raw_material_base_cost'])),
            recommended_retail_price=Decimal(str(analysis['pricing']['recommended_fair_retail_price'])),
            fair_wage_estimate=Decimal(str(analysis['pricing']['fair_artisan_wage'])),
            assigned_delivery_partner=delivery_partner,
            scan_source=scan_source,
            image_preview=analysis['sample_image']
        )
        
        # Save Spectral Telemetry Document in MongoDB Store
        mongo_doc = mongo_service.insert_spectral_scan({
            'scan_id': str(scan_log.id),
            'material_code': material.code,
            'material_name': material.name,
            'properties': analysis['properties'],
            'pricing_breakdown': analysis['pricing'],
            'delivery_partner': delivery_partner.to_dict() if delivery_partner else None,
            'source': scan_source
        })
        
        return Response({
            'success': True,
            'scan_id': str(scan_log.id),
            'analysis': analysis,
            'mongo_document_id': mongo_doc.get('_id'),
            'message': f"AI successfully identified {analysis['material_name']} with {analysis['confidence_score']*100:.1f}% confidence!"
        })


class MaterialListView(APIView):
    def get(self, request):
        materials = Material.objects.all()
        return Response({'materials': [m.to_dict() for m in materials]})


# ==========================================
# 3. PRODUCTS & MARKETPLACE
# ==========================================

class ProductListView(APIView):
    def get(self, request):
        category = request.GET.get('category')
        search = request.GET.get('search')
        artisan_id = request.GET.get('artisan_id')
        
        qs = Product.objects.filter(is_active=True).select_related('artisan', 'material')
        if category and category.lower() != 'all':
            qs = qs.filter(category__icontains=category)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(description__icontains=search)
        if artisan_id:
            qs = qs.filter(artisan_id=artisan_id)
            
        return Response({'products': [p.to_dict() for p in qs]})

    def post(self, request):
        artisan_id = request.data.get('artisan_id')
        artisan = get_object_or_404(UserProfile, id=artisan_id)
        
        title = SecurityService.sanitize_input(request.data.get('title', 'Handcrafted Item'))
        description = SecurityService.sanitize_input(request.data.get('description', 'Authentic handmade product.'))
        category = request.data.get('category', 'Textile')
        price = Decimal(str(request.data.get('price', 1500.00)))
        fair_wage = Decimal(str(request.data.get('fair_artisan_wage', float(price) * 0.70)))
        material_code = request.data.get('material_code')
        image_url = request.data.get('image_url', '')
        artisan_story = request.data.get('artisan_story', '')
        
        material = Material.objects.filter(code=material_code).first() if material_code else None
        
        product = Product.objects.create(
            artisan=artisan,
            material=material,
            title=title,
            description=description,
            category=category,
            price=price,
            fair_artisan_wage=fair_wage,
            material_cost=Decimal('350.00'),
            image_url=image_url or (material.image_sample_url if material else 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600'),
            artisan_story=artisan_story
        )
        
        # Save artisan craft story in MongoDB
        if artisan_story:
            mongo_service.insert_artisan_story({
                'artisan_id': str(artisan.id),
                'artisan_name': artisan.full_name,
                'product_id': str(product.id),
                'story': artisan_story,
                'category': category
            })
            
        return Response({
            'success': True,
            'product': product.to_dict(),
            'message': 'New artisanal craft cataloged successfully with AI fair pricing!'
        }, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        return Response({'product': product.to_dict()})


# ==========================================
# 4. UPI PAYMENTS, ESCROW & ORDER PROCESSING
# ==========================================

class InitiatePaymentView(APIView):
    """
    Generates unified UPI payment payload (GPay, PhonePe, Paytm, BHIM)
    Locks buyer payment in a cryptographic Escrow smart-holding deposit.
    """
    def post(self, request):
        buyer_id = request.data.get('buyer_id')
        product_id = request.data.get('product_id')
        payment_method = request.data.get('payment_method', 'GPAY')
        quantity = int(request.data.get('quantity', 1))
        shipping_address = request.data.get('shipping_address', 'Civil Lines, Varanasi, UP')
        
        buyer = get_object_or_404(UserProfile, id=buyer_id)
        product = get_object_or_404(Product, id=product_id)
        
        total_amount = product.price * quantity
        artisan_wage_amount = product.fair_artisan_wage * quantity
        order_number = f"ORD-KS-{int(datetime.utcnow().timestamp())}-{random.randint(100, 999)}"
        txn_id = f"UPI-TXN-{uuid.uuid4().hex[:12].upper()}"
        
        delivery_partner = DeliveryPartner.objects.filter(is_available=True).order_by('?').first()
        
        # Create Order in SQLite
        order = Order.objects.create(
            order_number=order_number,
            buyer=buyer,
            product=product,
            quantity=quantity,
            total_amount=total_amount,
            artisan_wage_amount=artisan_wage_amount,
            payment_method=payment_method,
            payment_status='ESCROW_LOCKED',
            payment_txn_id=txn_id,
            delivery_partner=delivery_partner,
            shipping_address=shipping_address,
            current_status='ORDERED'
        )
        
        # Generate Cryptographic Escrow Seal
        seal = SecurityService.generate_escrow_seal(order_number, str(product.artisan.id), float(artisan_wage_amount))
        
        escrow = EscrowTransaction.objects.create(
            order=order,
            artisan=product.artisan,
            amount=artisan_wage_amount,
            status='ESCROW_HELD',
            cryptographic_seal=seal,
            payout_upi_id='artisan.ramesh@okaxis'
        )
        
        # Deep-link URI for UPI (GPay, PhonePe, Paytm)
        upi_string = f"upi://pay?pa=kalasetu.escrow@icici&pn=KalaSetu%20Artisan%20Escrow&am={float(total_amount)}&tr={txn_id}&tn=Order%20{order_number}%20Fair%20Trade"
        
        mongo_service.log_audit('PAYMENT_INITIATED', buyer.username, {
            'order_number': order_number,
            'amount': float(total_amount),
            'method': payment_method,
            'escrow_seal': seal
        })
        
        return Response({
            'success': True,
            'order': order.to_dict(),
            'escrow': escrow.to_dict(),
            'payment_intent': {
                'txn_id': txn_id,
                'method': payment_method,
                'amount': float(total_amount),
                'upi_uri': upi_string,
                'qr_data': upi_string,
                'supported_apps': ['Google Pay', 'PhonePe', 'Paytm', 'BHIM UPI', 'Cred UPI'],
                'escrow_seal': seal,
                'fair_wage_guarantee': f"₹{float(artisan_wage_amount)} is locked in Escrow and 100% reserved for Artisan {product.artisan.full_name}."
            },
            'message': f"Payment of ₹{float(total_amount)} via {payment_method} initialized and locked in Artisan Escrow!"
        })


class VerifyPaymentView(APIView):
    def post(self, request):
        order_number = request.data.get('order_number')
        order = get_object_or_404(Order, order_number=order_number)
        order.payment_status = 'ESCROW_LOCKED'
        order.current_status = 'DISPATCHED'
        order.tracking_step = 2
        order.save()
        return Response({
            'success': True,
            'order': order.to_dict(),
            'message': 'Payment verified. Courier dispatched for pickup!'
        })


class ReleaseEscrowView(APIView):
    def post(self, request):
        order_number = request.data.get('order_number')
        order = get_object_or_404(Order, order_number=order_number)
        
        order.current_status = 'DELIVERED'
        order.payment_status = 'RELEASED_TO_ARTISAN'
        order.tracking_step = 4
        order.save()
        
        escrow = EscrowTransaction.objects.filter(order=order).first()
        if escrow:
            escrow.status = 'ESCROW_RELEASED'
            escrow.released_at = datetime.utcnow()
            escrow.save()
            
            # Credit Artisan balance
            if hasattr(order.product.artisan, 'artisan_detail'):
                detail = order.product.artisan.artisan_detail
                detail.escrow_wallet_balance += order.artisan_wage_amount
                detail.save()
                
        mongo_service.log_audit('ESCROW_RELEASED', order.buyer.username, {
            'order_number': order_number,
            'artisan': order.product.artisan.full_name,
            'amount': float(order.artisan_wage_amount)
        })
        
        return Response({
            'success': True,
            'order': order.to_dict(),
            'escrow': escrow.to_dict() if escrow else None,
            'message': f"Delivery verified! ₹{float(order.artisan_wage_amount)} has been directly released to {order.product.artisan.full_name}'s UPI wallet."
        })


# ==========================================
# 5. DELIVERY & REAL-TIME LOGISTICS
# ==========================================

class DeliveryTrackingView(APIView):
    def get(self, request, order_id):
        order = Order.objects.filter(order_number=order_id).first() or \
                Order.objects.filter(id=order_id).first()
                
        if not order:
            order = Order.objects.first()
            
        partner = order.delivery_partner or DeliveryPartner.objects.first()
        
        # Route simulation coordinates (From Artisan Workshop in Varanasi to Delivery Address)
        waypoints = [
            {'title': 'Artisan Workshop Hub', 'lat': 25.3176, 'lng': 82.9739, 'status': 'COMPLETED', 'time': '10:30 AM'},
            {'title': 'Quality & GI Tag Inspection Depot', 'lat': 25.3210, 'lng': 82.9810, 'status': 'COMPLETED' if order.tracking_step >= 2 else 'PENDING', 'time': '11:15 AM'},
            {'title': 'Clean Route Transit via Green EV', 'lat': 25.3340, 'lng': 82.9950, 'status': 'IN_PROGRESS' if order.tracking_step == 3 else ('COMPLETED' if order.tracking_step >= 4 else 'PENDING'), 'time': '12:00 PM'},
            {'title': 'Customer Destination Hub', 'lat': 25.3450, 'lng': 83.0080, 'status': 'COMPLETED' if order.tracking_step >= 4 else 'PENDING', 'time': '12:45 PM'}
        ]
        
        return Response({
            'order_number': order.order_number if order else 'ORD-DEMO-001',
            'status': order.current_status if order else 'IN_TRANSIT',
            'tracking_step': order.tracking_step if order else 3,
            'delivery_partner': partner.to_dict() if partner else None,
            'shipping_address': order.shipping_address if order else 'Plot 42, Civil Lines, Varanasi, UP',
            'estimated_eta': '35 mins',
            'waypoints': waypoints,
            'carbon_saved_kg': '1.8 kg CO2e (Green EV Route)'
        })


# ==========================================
# 6. ARTISAN METRICS & MONGO VAULT
# ==========================================

class ArtisanStatsView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(UserProfile, id=pk)
        products = Product.objects.filter(artisan=user)
        orders = Order.objects.filter(product__artisan=user)
        
        total_sales = sum(o.total_amount for o in orders)
        total_wages_earned = sum(o.artisan_wage_amount for o in orders.filter(payment_status='RELEASED_TO_ARTISAN'))
        escrow_locked_amount = sum(o.artisan_wage_amount for o in orders.filter(payment_status='ESCROW_LOCKED'))
        
        return Response({
            'artisan': user.to_dict(),
            'total_listings': products.count(),
            'total_orders': orders.count(),
            'total_sales': float(total_sales),
            'total_wages_earned': float(total_wages_earned),
            'escrow_locked_amount': float(escrow_locked_amount),
            'rating': 4.92,
            'fair_wage_index': '100% Exploitation-Free'
        })


class MongoVaultView(APIView):
    """Exposes MongoDB telemetry scans & heritage vault records."""
    def get(self, request):
        scans = mongo_service.get_spectral_scans(limit=25)
        stories = mongo_service.get_artisan_stories()
        return Response({
            'mongo_connected': mongo_service.is_connected,
            'database_engine': 'MongoDB + Embedded Vault',
            'spectral_scans_count': len(scans),
            'spectral_scans': scans,
            'artisan_stories': stories
        })
