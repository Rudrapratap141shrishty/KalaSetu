"""
Graphene GraphQL Schema for Smart Cataloging & AI Material Retrieval
Defines GraphQL types, queries, and mutations for scanning materials, retrieving properties,
costs, assigned delivery persons, and handling orders.
"""

import graphene
from graphene_django import DjangoObjectType
from .models import (
    UserProfile, ArtisanProfile, Material,
    MaterialScanLog, Product, DeliveryPartner, Order, EscrowTransaction
)
from .ai_vision_engine import AIVisionEngine
from .mongo_service import mongo_service
import json

# --- GraphQL Types ---

class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ArtisanProfileType(DjangoObjectType):
    class Meta:
        model = ArtisanProfile
        fields = '__all__'

class MaterialType(DjangoObjectType):
    class Meta:
        model = Material
        fields = '__all__'

class DeliveryPartnerType(DjangoObjectType):
    class Meta:
        model = DeliveryPartner
        fields = '__all__'

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'

class EscrowTransactionType(DjangoObjectType):
    class Meta:
        model = EscrowTransaction
        fields = '__all__'

# Custom Type for AI Scan Results with Pricing & Delivery
class PricingBreakdownType(graphene.ObjectType):
    raw_material_base_cost = graphene.Float()
    standard_craft_weight_kg = graphene.Float()
    standard_labor_hours = graphene.Float()
    fair_hourly_wage = graphene.Float()
    fair_artisan_wage = graphene.Float()
    tooling_and_firing = graphene.Float()
    eco_packaging_and_tax = graphene.Float()
    recommended_fair_retail_price = graphene.Float()
    conventional_middleman_price = graphene.Float()
    artisan_direct_share_percent = graphene.Float()
    currency = graphene.String()

class AIScanResultType(graphene.ObjectType):
    material_key = graphene.String()
    material_code = graphene.String()
    material_name = graphene.String()
    category = graphene.String()
    origin_region = graphene.String()
    gi_certified = graphene.Boolean()
    confidence_score = graphene.Float()
    tensile_strength = graphene.String()
    durability_years = graphene.Int()
    carbon_footprint_score = graphene.String()
    texture_spec = graphene.String()
    properties_json = graphene.String()
    suggested_crafts = graphene.List(graphene.String)
    sample_image = graphene.String()
    pricing = graphene.Field(PricingBreakdownType)
    assigned_delivery = graphene.Field(DeliveryPartnerType)


# --- Root Query ---

class Query(graphene.ObjectType):
    # Material Scanning Query
    scan_material = graphene.Field(
        AIScanResultType,
        material_hint=graphene.String(default_value='TERRACOTTA_CLAY'),
        description="Scans artisanal material and returns properties, fair-cost breakdown, and assigned delivery partner"
    )
    
    # Catalog & Materials
    all_materials = graphene.List(MaterialType)
    material_by_code = graphene.Field(MaterialType, code=graphene.String(required=True))
    
    # Products & Marketplace
    all_products = graphene.List(ProductType, category=graphene.String(), search=graphene.String())
    product_by_id = graphene.Field(ProductType, id=graphene.String(required=True))
    
    # Artisans & Delivery
    all_artisans = graphene.List(ArtisanProfileType)
    all_delivery_partners = graphene.List(DeliveryPartnerType)
    assigned_delivery_partner = graphene.Field(DeliveryPartnerType, partner_id=graphene.String())
    
    # Orders & Escrows
    orders_by_buyer = graphene.List(OrderType, buyer_id=graphene.String(required=True))
    order_by_number = graphene.Field(OrderType, order_number=graphene.String(required=True))
    escrow_transactions = graphene.List(EscrowTransactionType)

    def resolve_scan_material(self, info, material_hint):
        analysis = AIVisionEngine.analyze_image_or_sample(hint_name=material_hint)
        
        # Log to MongoDB document layer
        mongo_service.insert_spectral_scan({
            'material_name': analysis['material_name'],
            'category': analysis['category'],
            'origin': analysis['origin_region'],
            'properties': analysis['properties'],
            'pricing': analysis['pricing'],
            'source': 'GraphQL_Scan_Resolver'
        })
        
        # Build Pricing Breakdown GraphQL Object
        p = analysis['pricing']
        pricing_obj = PricingBreakdownType(
            raw_material_base_cost=p['raw_material_base_cost'],
            standard_craft_weight_kg=p['standard_craft_weight_kg'],
            standard_labor_hours=p['standard_labor_hours'],
            fair_hourly_wage=p['fair_hourly_wage'],
            fair_artisan_wage=p['fair_artisan_wage'],
            tooling_and_firing=p['tooling_and_firing'],
            eco_packaging_and_tax=p['eco_packaging_and_tax'],
            recommended_fair_retail_price=p['recommended_fair_retail_price'],
            conventional_middleman_price=p['conventional_middleman_price'],
            artisan_direct_share_percent=p['artisan_direct_share_percent'],
            currency=p['currency']
        )
        
        # Find or use delivery partner
        del_data = analysis['assigned_delivery']
        partner = DeliveryPartner.objects.filter(name=del_data.get('name')).first()
        if not partner:
            partner = DeliveryPartner.objects.first()

        return AIScanResultType(
            material_key=analysis['material_key'],
            material_code=analysis['material_code'],
            material_name=analysis['material_name'],
            category=analysis['category'],
            origin_region=analysis['origin_region'],
            gi_certified=analysis['gi_certified'],
            confidence_score=analysis['confidence_score'],
            tensile_strength=analysis['tensile_strength'],
            durability_years=analysis['durability_years'],
            carbon_footprint_score=analysis['carbon_footprint_score'],
            texture_spec=analysis['texture_spec'],
            properties_json=json.dumps(analysis['properties']),
            suggested_crafts=analysis['suggested_crafts'],
            sample_image=analysis['sample_image'],
            pricing=pricing_obj,
            assigned_delivery=partner
        )

    def resolve_all_materials(self, info):
        return Material.objects.all()

    def resolve_material_by_code(self, info, code):
        return Material.objects.filter(code=code).first()

    def resolve_all_products(self, info, category=None, search=None):
        qs = Product.objects.filter(is_active=True).select_related('artisan', 'material')
        if category and category.lower() != 'all':
            qs = qs.filter(category__icontains=category)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(description__icontains=search)
        return qs

    def resolve_product_by_id(self, info, id):
        return Product.objects.filter(id=id).first()

    def resolve_all_artisans(self, info):
        return ArtisanProfile.objects.select_related('user').all()

    def resolve_all_delivery_partners(self, info):
        return DeliveryPartner.objects.all()

    def resolve_orders_by_buyer(self, info, buyer_id):
        return Order.objects.filter(buyer_id=buyer_id).order_by('-created_at')

    def resolve_order_by_number(self, info, order_number):
        return Order.objects.filter(order_number=order_number).first()

    def resolve_escrow_transactions(self, info):
        return EscrowTransaction.objects.select_related('order', 'artisan').all()


# --- GraphQL Mutations ---

class ScanMaterialMutation(graphene.Mutation):
    class Arguments:
        material_hint = graphene.String(required=True)
        scan_source = graphene.String(default_value='AI_MOBILE_CAMERA')

    result = graphene.Field(AIScanResultType)
    success = graphene.Boolean()

    def mutate(self, info, material_hint, scan_source='AI_MOBILE_CAMERA'):
        analysis = AIVisionEngine.analyze_image_or_sample(hint_name=material_hint)
        p = analysis['pricing']
        pricing_obj = PricingBreakdownType(
            raw_material_base_cost=p['raw_material_base_cost'],
            standard_craft_weight_kg=p['standard_craft_weight_kg'],
            standard_labor_hours=p['standard_labor_hours'],
            fair_hourly_wage=p['fair_hourly_wage'],
            fair_artisan_wage=p['fair_artisan_wage'],
            tooling_and_firing=p['tooling_and_firing'],
            eco_packaging_and_tax=p['eco_packaging_and_tax'],
            recommended_fair_retail_price=p['recommended_fair_retail_price'],
            conventional_middleman_price=p['conventional_middleman_price'],
            artisan_direct_share_percent=p['artisan_direct_share_percent'],
            currency=p['currency']
        )
        partner = DeliveryPartner.objects.first()
        res = AIScanResultType(
            material_key=analysis['material_key'],
            material_code=analysis['material_code'],
            material_name=analysis['material_name'],
            category=analysis['category'],
            origin_region=analysis['origin_region'],
            gi_certified=analysis['gi_certified'],
            confidence_score=analysis['confidence_score'],
            tensile_strength=analysis['tensile_strength'],
            durability_years=analysis['durability_years'],
            carbon_footprint_score=analysis['carbon_footprint_score'],
            texture_spec=analysis['texture_spec'],
            properties_json=json.dumps(analysis['properties']),
            suggested_crafts=analysis['suggested_crafts'],
            sample_image=analysis['sample_image'],
            pricing=pricing_obj,
            assigned_delivery=partner
        )
        return ScanMaterialMutation(result=res, success=True)


class Mutation(graphene.ObjectType):
    scan_material = ScanMaterialMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
