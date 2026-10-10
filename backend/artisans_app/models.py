from django.db import models
import uuid
import json

class RoleChoices(models.TextChoices):
    ARTISAN = 'ARTISAN', 'Marginalized Artisan / Creator'
    CLIENT_B2B = 'CLIENT_B2B', 'Client / B2B Wholesaler / NGO'
    BUYER_USER = 'BUYER_USER', 'Consumer / Craft Enthusiast'
    DELIVERY_AGENT = 'DELIVERY_AGENT', 'Logistics & Delivery Partner'

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=RoleChoices.choices, default=RoleChoices.ARTISAN)
    phone = models.CharField(max_length=20, default='+91 98765 43210')
    city = models.CharField(max_length=100, default='Varanasi')
    state = models.CharField(max_length=100, default='Uttar Pradesh')
    avatar_url = models.CharField(max_length=500, blank=True, default='')
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'city': self.city,
            'state': self.state,
            'avatar_url': self.avatar_url,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ArtisanProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='artisan_detail')
    craft_type = models.CharField(max_length=120, default='Handloom Zari Weaving')
    community_name = models.CharField(max_length=150, default='Bunkar Sahakari Samiti')
    gi_tag_number = models.CharField(max_length=80, default='GI-IN-2009-082')
    experience_years = models.IntegerField(default=18)
    voice_pref_language = models.CharField(max_length=50, default='hi-IN')
    escrow_wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=24500.00)
    bank_upi_id = models.CharField(max_length=100, default='artisan.ramesh@okaxis')
    rating = models.FloatField(default=4.9)
    bio = models.TextField(default='Traditional artisan with over 18 years crafting authentic heritage pieces with pure natural materials.')

    def __str__(self):
        return f"Artisan: {self.user.full_name} - {self.craft_type}"

    def to_dict(self):
        return {
            'id': str(self.id),
            'user': self.user.to_dict(),
            'craft_type': self.craft_type,
            'community_name': self.community_name,
            'gi_tag_number': self.gi_tag_number,
            'experience_years': self.experience_years,
            'voice_pref_language': self.voice_pref_language,
            'escrow_wallet_balance': float(self.escrow_wallet_balance),
            'bank_upi_id': self.bank_upi_id,
            'rating': self.rating,
            'bio': self.bio
        }


class Material(models.Model):
    CATEGORY_CHOICES = [
        ('TEXTILE', 'Natural Textile & Silk'),
        ('POTTERY', 'Clay & Glazed Ceramic'),
        ('WOODWORK', 'Hardwood & Carving Wood'),
        ('METAL', 'Brass, Bell Metal & Dokra'),
        ('LEATHER', 'Vegetable-Tanned Leather'),
        ('CANE_BAMBOO', 'Cane, Bamboo & Grass'),
        ('PAINTING', 'Natural Mineral Pigments & Gold Leaf'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='TEXTILE')
    origin_region = models.CharField(max_length=150)
    gi_certified = models.BooleanField(default=True)
    standard_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost in INR")
    unit = models.CharField(max_length=30, default='kg')
    carbon_footprint_score = models.CharField(max_length=20, default='A+ (0.3 kg CO2e)')
    tensile_strength = models.CharField(max_length=100, default='High (Grade AAA)')
    durability_years = models.IntegerField(default=25)
    texture_spec = models.TextField(default='Natural hand-spun fiber with distinct warp-weft texture')
    spectral_hash = models.CharField(max_length=128, default='SPEC-9821-OCT-771')
    image_sample_url = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.origin_region})"

    def to_dict(self):
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'origin_region': self.origin_region,
            'gi_certified': self.gi_certified,
            'standard_cost_per_unit': float(self.standard_cost_per_unit),
            'unit': self.unit,
            'carbon_footprint_score': self.carbon_footprint_score,
            'tensile_strength': self.tensile_strength,
            'durability_years': self.durability_years,
            'texture_spec': self.texture_spec,
            'spectral_hash': self.spectral_hash,
            'image_sample_url': self.image_sample_url
        }


class DeliveryPartner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, default='+91 91234 56789')
    vehicle_type = models.CharField(max_length=80, default='Eco EV Cargo Van')
    vehicle_number = models.CharField(max_length=30, default='UP-65-AK-4421')
    hub_city = models.CharField(max_length=100, default='Varanasi Craft Hub')
    current_lat = models.FloatField(default=25.3176)
    current_lng = models.FloatField(default=82.9739)
    rating = models.FloatField(default=4.85)
    total_trips = models.IntegerField(default=412)
    is_available = models.BooleanField(default=True)
    estimated_dispatch_mins = models.IntegerField(default=15)

    def __str__(self):
        return f"{self.name} ({self.vehicle_type} - {self.hub_city})"

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'phone': self.phone,
            'vehicle_type': self.vehicle_type,
            'vehicle_number': self.vehicle_number,
            'hub_city': self.hub_city,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'rating': self.rating,
            'total_trips': self.total_trips,
            'is_available': self.is_available,
            'estimated_dispatch_mins': self.estimated_dispatch_mins
        }


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artisan = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='products')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    title = models.CharField(max_length=250)
    description = models.TextField()
    category = models.CharField(max_length=80, default='Textile')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fair_artisan_wage = models.DecimalField(max_digits=10, decimal_places=2)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock_quantity = models.IntegerField(default=10)
    badge = models.CharField(max_length=100, default='GI Authenticated 100% Handcrafted')
    image_url = models.CharField(max_length=500, blank=True, default='')
    artisan_story = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ₹{self.price}"

    def to_dict(self):
        return {
            'id': str(self.id),
            'artisan_id': str(self.artisan.id),
            'artisan_name': self.artisan.full_name,
            'artisan_city': self.artisan.city,
            'material': self.material.to_dict() if self.material else None,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': float(self.price),
            'fair_artisan_wage': float(self.fair_artisan_wage),
            'material_cost': float(self.material_cost),
            'stock_quantity': self.stock_quantity,
            'badge': self.badge,
            'image_url': self.image_url,
            'artisan_story': self.artisan_story,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MaterialScanLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='scan_logs')
    confidence_score = models.FloatField(default=0.96)
    detected_properties_json = models.TextField(default='{}')
    estimated_base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    fair_wage_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    assigned_delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True)
    scan_source = models.CharField(max_length=50, default='AI_LIVE_CAMERA')
    image_preview = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan: {self.material.name} ({self.confidence_score*100:.1f}%)"

    def get_detected_properties(self):
        try:
            return json.loads(self.detected_properties_json)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': str(self.id),
            'material': self.material.to_dict(),
            'confidence_score': self.confidence_score,
            'detected_properties': self.get_detected_properties(),
            'estimated_base_cost': float(self.estimated_base_cost),
            'recommended_retail_price': float(self.recommended_retail_price),
            'fair_wage_estimate': float(self.fair_wage_estimate),
            'assigned_delivery_partner': self.assigned_delivery_partner.to_dict() if self.assigned_delivery_partner else None,
            'scan_source': self.scan_source,
            'image_preview': self.image_preview,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('GPAY', 'Google Pay (GPay)'),
        ('PHONEPE', 'PhonePe UPI'),
        ('PAYTM', 'Paytm Wallet & UPI'),
        ('BHIM', 'BHIM UPI'),
        ('CARD', 'Credit / Debit Card (RuPay/Visa/MasterCard)'),
        ('NETBANKING', 'Internet Banking'),
        ('COD_ESCROW', 'Cash On Delivery with Fair-Trade Escrow'),
    ]

    STATUS_CHOICES = [
        ('ORDERED', 'Order Placed & Escrow Funded'),
        ('DISPATCHED', 'Picked up by Courier'),
        ('IN_TRANSIT', 'In Transit via Clean Route'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered & Escrow Released'),
        ('CANCELLED', 'Cancelled & Escrow Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=40, unique=True)
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_bought')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    artisan_wage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='GPAY')
    payment_status = models.CharField(max_length=30, default='ESCROW_LOCKED')
    payment_txn_id = models.CharField(max_length=100, default='')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.TextField(default='Plot 42, Heritage Enclave, Civil Lines, Varanasi, UP')
    current_status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='ORDERED')
    tracking_step = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} - ₹{self.total_amount}"

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'buyer': self.buyer.to_dict(),
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'total_amount': float(self.total_amount),
            'artisan_wage_amount': float(self.artisan_wage_amount),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'payment_txn_id': self.payment_txn_id,
            'delivery_partner': self.delivery_partner.to_dict() if self.delivery_partner else None,
            'shipping_address': self.shipping_address,
            'current_status': self.current_status,
            'tracking_step': self.tracking_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EscrowTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='escrow_ledger')
    artisan = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='escrow_credits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, default='ESCROW_HELD')
    cryptographic_seal = models.CharField(max_length=128, default='')
    payout_upi_id = models.CharField(max_length=100, default='artisan.ramesh@okaxis')
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Escrow ₹{self.amount} for Order {self.order.order_number} ({self.status})"

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_number': self.order.order_number,
            'artisan_name': self.artisan.full_name,
            'amount': float(self.amount),
            'status': self.status,
            'cryptographic_seal': self.cryptographic_seal,
            'payout_upi_id': self.payout_upi_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'released_at': self.released_at.isoformat() if self.released_at else None
        }
