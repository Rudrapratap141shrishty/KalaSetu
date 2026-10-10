"""
Seed Data Generator for KalaSetu Artisan Market Linkage App
Populates authentic traditional materials, artisans, products, delivery partners, and initial orders.
"""

from decimal import Decimal
from .models import (
    UserProfile, ArtisanProfile, Material,
    Product, DeliveryPartner, Order, EscrowTransaction, RoleChoices
)
from .security import SecurityService
from .mongo_service import mongo_service
import random

def seed_database():
    print("[Seed] Seeding authentic artisan ecosystem...")
    
    # 1. Seed Delivery Partners
    partners_data = [
        {
            'name': 'Devendra Kumar (EV Cargo)',
            'phone': '+91 98112 34567',
            'vehicle_type': 'Green Electric Cargo Van',
            'vehicle_number': 'UP-65-EV-1088',
            'hub_city': 'Varanasi Central Artisan Hub',
            'current_lat': 25.3176,
            'current_lng': 82.9739,
            'rating': 4.92,
            'total_trips': 520,
            'estimated_dispatch_mins': 12
        },
        {
            'name': 'Pooja Sharma (Speed Hub)',
            'phone': '+91 97234 88901',
            'vehicle_type': 'Electric Scooter Cargo',
            'vehicle_number': 'RJ-14-EC-4412',
            'hub_city': 'Jaipur Crafts Cluster',
            'current_lat': 26.9124,
            'current_lng': 75.7873,
            'rating': 4.88,
            'total_trips': 380,
            'estimated_dispatch_mins': 15
        },
        {
            'name': 'Mangal Murmu (Tribal Express)',
            'phone': '+91 94311 67200',
            'vehicle_type': 'All-Terrain Green Van',
            'vehicle_number': 'CG-04-TR-9021',
            'hub_city': 'Bastar Tribal Collective Depot',
            'current_lat': 19.0760,
            'current_lng': 82.0298,
            'rating': 4.95,
            'total_trips': 410,
            'estimated_dispatch_mins': 20
        }
    ]
    
    delivery_objs = []
    for pd in partners_data:
        partner, _ = DeliveryPartner.objects.get_or_create(
            name=pd['name'],
            defaults=pd
        )
        delivery_objs.append(partner)
    print(f"[Seed] {len(delivery_objs)} Delivery Partners verified.")

    # 2. Seed Standard GI Materials
    materials_data = [
        {
            'code': 'MAT-TERRA-01',
            'name': 'GI Gorakhpur Natural Terracotta Clay',
            'category': 'POTTERY',
            'origin_region': 'Gorakhpur, Uttar Pradesh',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('45.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A+ (0.15 kg CO2e / kg)',
            'tensile_strength': 'Compressive 18.5 MPa',
            'durability_years': 30,
            'texture_spec': 'Fine alluvial clay, fired at 850°C, natural iron-oxide red hue',
            'spectral_hash': 'SPEC-TERRA-991',
            'image_sample_url': 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600&auto=format&fit=crop&q=80'
        },
        {
            'code': 'MAT-SILK-02',
            'name': 'Pure Katan Mulberry Silk with Real Zari',
            'category': 'TEXTILE',
            'origin_region': 'Varanasi, Uttar Pradesh',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('4200.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A (0.85 kg CO2e / m)',
            'tensile_strength': 'Grade AAA+ (4.8 cN/dtex)',
            'durability_years': 50,
            'texture_spec': 'Intertwined warp-weft handloom weave with gold-silver electroplated thread',
            'spectral_hash': 'SPEC-SILK-442',
            'image_sample_url': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80'
        },
        {
            'code': 'MAT-TEAK-03',
            'name': 'Seasoned Saharanpur Carving Teak Hardwood',
            'category': 'WOODWORK',
            'origin_region': 'Saharanpur, Uttar Pradesh',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('280.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A+ (Net Carbon Negative Biomass)',
            'tensile_strength': 'Janka Hardness 1,070 lbf',
            'durability_years': 60,
            'texture_spec': 'Dense straight-grain hardwood with natural teak oils and warm honey tones',
            'spectral_hash': 'SPEC-WOOD-301',
            'image_sample_url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80'
        },
        {
            'code': 'MAT-DHOKRA-04',
            'name': 'Bastar Lost-Wax Bell Metal & Brass Alloy',
            'category': 'METAL',
            'origin_region': 'Bastar, Chhattisgarh',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('650.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A (1.2 kg CO2e / kg)',
            'tensile_strength': '380 MPa (Cast Bell Metal)',
            'durability_years': 100,
            'texture_spec': 'Intricate wax-thread relief with antique olive-gold rustic patina',
            'spectral_hash': 'SPEC-DHOKRA-880',
            'image_sample_url': 'https://images.unsplash.com/photo-1606744888344-498238f01761?w=600&auto=format&fit=crop&q=80'
        },
        {
            'code': 'MAT-BAGRU-05',
            'name': 'Bagru Organic Handblock Indigo Cotton',
            'category': 'TEXTILE',
            'origin_region': 'Bagru, Rajasthan',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('380.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A+ (0.28 kg CO2e / m)',
            'tensile_strength': 'Natural Long-Staple Cotton (GSM 125)',
            'durability_years': 15,
            'texture_spec': 'Unbleached hand-spun cotton dyed with fermented natural indigo',
            'spectral_hash': 'SPEC-BAGRU-120',
            'image_sample_url': 'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?w=600&auto=format&fit=crop&q=80'
        },
        {
            'code': 'MAT-BLUEPOT-06',
            'name': 'Jaipur Quartz Stone Glazed Blue Ceramic',
            'category': 'POTTERY',
            'origin_region': 'Jaipur, Rajasthan',
            'gi_certified': True,
            'standard_cost_per_unit': Decimal('190.00'),
            'unit': 'kg',
            'carbon_footprint_score': 'A (0.45 kg CO2e / pc)',
            'tensile_strength': 'Vitrified Low-Shrinkage Composite',
            'durability_years': 40,
            'texture_spec': 'Lustrous cobalt-blue and turquoise glaze over pure crushed quartz matrix',
            'spectral_hash': 'SPEC-BLUEPOT-711',
            'image_sample_url': 'https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=600&auto=format&fit=crop&q=80'
        }
    ]
    
    material_map = {}
    for md in materials_data:
        mat, _ = Material.objects.get_or_create(code=md['code'], defaults=md)
        material_map[md['code']] = mat
    print(f"[Seed] {len(material_map)} Materials indexed.")

    # 3. Seed Users & Diverse Marginalized Artisans
    artisan_users_data = [
        {
            'username': 'ramesh_weaver',
            'full_name': 'Ramesh Kumar Ansari',
            'email': 'ramesh.artisan@kalasetu.org',
            'role': RoleChoices.ARTISAN,
            'phone': '+91 98390 11223',
            'city': 'Varanasi',
            'state': 'Uttar Pradesh',
            'craft_type': 'Banarasi Brocade & Zari Handloom',
            'community_name': 'Madhyanchal Bunkar Samiti',
            'gi_tag_number': 'GI-IN-2009-082',
            'experience_years': 24,
            'escrow_wallet_balance': Decimal('38400.00'),
            'bank_upi_id': 'ramesh.weaver@okaxis',
            'bio': '4th generation master weaver preserving 400-year-old Kadwa handloom technique on pure mulberry silk.'
        },
        {
            'username': 'savitri_potter',
            'full_name': 'Savitri Prajapati',
            'email': 'savitri.clay@kalasetu.org',
            'role': RoleChoices.ARTISAN,
            'phone': '+91 94520 88711',
            'city': 'Gorakhpur',
            'state': 'Uttar Pradesh',
            'craft_type': 'GI Terracotta & Natural Clayware',
            'community_name': 'Kumbhakar Vikas Sangh',
            'gi_tag_number': 'GI-IN-2020-091',
            'experience_years': 19,
            'escrow_wallet_balance': Decimal('21200.00'),
            'bank_upi_id': 'savitri.terracotta@paytm',
            'bio': 'Award-winning traditional potter shaping non-toxic curative clay water dispensers and heritage temple artifacts.'
        },
        {
            'username': 'birju_dhokra',
            'full_name': 'Birju Korwa',
            'email': 'birju.bastar@kalasetu.org',
            'role': RoleChoices.ARTISAN,
            'phone': '+91 91114 99012',
            'city': 'Bastar',
            'state': 'Chhattisgarh',
            'craft_type': 'Tribal Lost-Wax Dhokra Bell Metal',
            'community_name': 'Korwa Tribal Artisan Guild',
            'gi_tag_number': 'GI-IN-2008-056',
            'experience_years': 22,
            'escrow_wallet_balance': Decimal('29800.00'),
            'bank_upi_id': 'birju.korwa@ybl',
            'bio': 'Tribal master craftsman casting ancient lost-wax bronze motifs honoring nature, wildlife, and village traditions.'
        },
        {
            'username': 'fatima_blockprint',
            'full_name': 'Fatima Bano Chippa',
            'email': 'fatima.bagru@kalasetu.org',
            'role': RoleChoices.ARTISAN,
            'phone': '+91 98291 55432',
            'city': 'Bagru',
            'state': 'Rajasthan',
            'craft_type': 'Natural Dabu Indigo Block Printing',
            'community_name': 'Chippa Artisan Federation',
            'gi_tag_number': 'GI-IN-2011-142',
            'experience_years': 16,
            'escrow_wallet_balance': Decimal('18500.00'),
            'bank_upi_id': 'fatima.dabu@okhdfcbank',
            'bio': 'Specialist in 100% organic indigo mud-resist Dabu printing on ethically sourced hand-spun cotton.'
        }
    ]

    artisan_map = {}
    for ud in artisan_users_data:
        user, _ = UserProfile.objects.get_or_create(
            username=ud['username'],
            defaults={
                'full_name': ud['full_name'],
                'email': ud['email'],
                'role': ud['role'],
                'phone': ud['phone'],
                'city': ud['city'],
                'state': ud['state'],
                'is_verified': True
            }
        )
        artisan_prof, _ = ArtisanProfile.objects.get_or_create(
            user=user,
            defaults={
                'craft_type': ud['craft_type'],
                'community_name': ud['community_name'],
                'gi_tag_number': ud['gi_tag_number'],
                'experience_years': ud['experience_years'],
                'escrow_wallet_balance': ud['escrow_wallet_balance'],
                'bank_upi_id': ud['bank_upi_id'],
                'bio': ud['bio']
            }
        )
        artisan_map[ud['username']] = user
    print(f"[Seed] {len(artisan_map)} Master Artisans created.")

    # 4. Seed Client B2B & Buyer Users
    b2b_client, _ = UserProfile.objects.get_or_create(
        username='fabindia_procure',
        defaults={
            'full_name': 'Ananya Sengupta (FairTrade Corp / NGO Lead)',
            'email': 'procure@fabcraft.org',
            'role': RoleChoices.CLIENT_B2B,
            'phone': '+91 99887 66554',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'is_verified': True
        }
    )
    
    buyer_user, _ = UserProfile.objects.get_or_create(
        username='arjun_buyer',
        defaults={
            'full_name': 'Arjun Mehra',
            'email': 'arjun.mehra@gmail.com',
            'role': RoleChoices.BUYER_USER,
            'phone': '+91 98711 22334',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'is_verified': True
        }
    )

    # 5. Seed Catalog Products
    products_data = [
        {
            'artisan_user': 'ramesh_weaver',
            'mat_code': 'MAT-SILK-02',
            'title': 'GI Varanasi Royal Shikargah Mulberry Silk Saree',
            'description': 'Handwoven on traditional pit loom with pure gold-silver electroplated zari motifs depicting royal flora & fauna.',
            'category': 'Textile',
            'price': Decimal('7850.00'),
            'fair_wage': Decimal('5200.00'),
            'material_cost': Decimal('1850.00'),
            'stock': 4,
            'badge': 'GI Certified • 100% Handloom',
            'image_url': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80',
            'story': 'Takes 48 painstaking hours on a manual wooden loom. Every purchase supports 4 weaver apprentice families in Varanasi.'
        },
        {
            'artisan_user': 'savitri_potter',
            'mat_code': 'MAT-TERRA-01',
            'title': 'Curative Terracotta Alkaline Water Dispenser (5L)',
            'description': 'Naturally cools and alkalizes drinking water without electricity. Hand-burnished with river pebbles for ultra-fine micro-porosity.',
            'category': 'Pottery',
            'price': Decimal('1850.00'),
            'fair_wage': Decimal('1250.00'),
            'material_cost': Decimal('220.00'),
            'stock': 15,
            'badge': 'Lead-Free • Eco-Therapeutic',
            'image_url': 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=600&auto=format&fit=crop&q=80',
            'story': 'Fired in ancestral community kilns using agricultural husk. 100% biodegradable and zero chemical glazes.'
        },
        {
            'artisan_user': 'birju_dhokra',
            'mat_code': 'MAT-DHOKRA-04',
            'title': 'Bastar Lost-Wax Tribal Musician Bell Metal Sculpture',
            'description': 'Cast using the 4,000-year-old lost wax method (Cire Perdue). Each piece is an irreplaceable original with no two identical casts.',
            'category': 'Metal',
            'price': Decimal('4200.00'),
            'fair_wage': Decimal('2850.00'),
            'material_cost': Decimal('850.00'),
            'stock': 6,
            'badge': 'Ancient Craft • 100% Recycled Bronze',
            'image_url': 'https://images.unsplash.com/photo-1606744888344-498238f01761?w=600&auto=format&fit=crop&q=80',
            'story': 'Birju Korwa and his clan gather wild bee wax from Bastar forests to weave delicate thread relief onto clay forms.'
        },
        {
            'artisan_user': 'fatima_blockprint',
            'mat_code': 'MAT-BAGRU-05',
            'title': 'Organic Indigo Dabu Handblock Printed Cotton Stole',
            'description': 'Fermented plant indigo resist-printed with hand-carved teak blocks. Breathable, colorfast, and skin-friendly.',
            'category': 'Textile',
            'price': Decimal('1650.00'),
            'fair_wage': Decimal('1100.00'),
            'material_cost': Decimal('320.00'),
            'stock': 20,
            'badge': 'Natural Dye • Zero Chemical',
            'image_url': 'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?w=600&auto=format&fit=crop&q=80',
            'story': 'Dyed in sunlit riverbanks of Bagru using heirloom wooden blocks passed down through three generations.'
        },
        {
            'artisan_user': 'savitri_potter',
            'mat_code': 'MAT-BLUEPOT-06',
            'title': 'Jaipur Turquoise Quartz Glazed Heritage Platter',
            'description': 'Unique non-clay formulation made of crushed quartz, Multani mitti, and natural cobalt minerals.',
            'category': 'Pottery',
            'price': Decimal('2350.00'),
            'fair_wage': Decimal('1600.00'),
            'material_cost': Decimal('410.00'),
            'stock': 8,
            'badge': 'Quartz Matrix • Royal Heritage',
            'image_url': 'https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=600&auto=format&fit=crop&q=80',
            'story': 'Low thermal expansion ensures everlasting luster without cracking.'
        },
        {
            'artisan_user': 'ramesh_weaver',
            'mat_code': 'MAT-TEAK-03',
            'title': 'Saharanpur Hand-Carved Jali Wood Keepsake Box',
            'description': 'Lattice floral woodwork crafted from single-plank seasoned teak hardwood with brass inlays.',
            'category': 'Woodwork',
            'price': Decimal('2800.00'),
            'fair_wage': Decimal('1850.00'),
            'material_cost': Decimal('550.00'),
            'stock': 12,
            'badge': 'Kiln Dried • 100% Solid Teak',
            'image_url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80',
            'story': 'Requires 16 hours of razor-sharp chisel carving by master artisans.'
        }
    ]

    product_objs = []
    for prod_data in products_data:
        art_user = artisan_map[prod_data['artisan_user']]
        mat_obj = material_map[prod_data['mat_code']]
        
        prod, _ = Product.objects.get_or_create(
            title=prod_data['title'],
            defaults={
                'artisan': art_user,
                'material': mat_obj,
                'description': prod_data['description'],
                'category': prod_data['category'],
                'price': prod_data['price'],
                'fair_artisan_wage': prod_data['fair_wage'],
                'material_cost': prod_data['material_cost'],
                'stock_quantity': prod_data['stock'],
                'badge': prod_data['badge'],
                'image_url': prod_data['image_url'],
                'artisan_story': prod_data['story']
            }
        )
        product_objs.append(prod)
        
        # Mirror story to MongoDB
        mongo_service.insert_artisan_story({
            'artisan_name': art_user.full_name,
            'craft_title': prod.title,
            'category': prod.category,
            'story': prod_data['story'],
            'gi_origin': mat_obj.origin_region
        })
    print(f"[Seed] {len(product_objs)} Heritage Products cataloged.")

    # 6. Seed Sample Active Order with Escrow
    if product_objs and delivery_objs:
        sample_prod = product_objs[0]
        sample_order, _ = Order.objects.get_or_create(
            order_number='ORD-KS-2026-8891',
            defaults={
                'buyer': buyer_user,
                'product': sample_prod,
                'quantity': 1,
                'total_amount': sample_prod.price,
                'artisan_wage_amount': sample_prod.fair_artisan_wage,
                'payment_method': 'GPAY',
                'payment_status': 'ESCROW_LOCKED',
                'payment_txn_id': 'UPI-TXN-984421-GPAY',
                'delivery_partner': delivery_objs[0],
                'shipping_address': 'Flat 304, Heritage Towers, Mumbai, MH',
                'current_status': 'IN_TRANSIT',
                'tracking_step': 3
            }
        )
        
        seal = SecurityService.generate_escrow_seal(sample_order.order_number, str(sample_prod.artisan.id), float(sample_prod.fair_artisan_wage))
        EscrowTransaction.objects.get_or_create(
            order=sample_order,
            defaults={
                'artisan': sample_prod.artisan,
                'amount': sample_prod.fair_artisan_wage,
                'status': 'ESCROW_HELD',
                'cryptographic_seal': seal,
                'payout_upi_id': 'ramesh.weaver@okaxis'
            }
        )
        print("[Seed] Verified Escrow Transaction created.")
    print("[Seed] Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
