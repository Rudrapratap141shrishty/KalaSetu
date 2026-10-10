# KalaSetu (कला सेतु) — AI-Driven Market Linkage & Smart Cataloging Mobile Application for Marginalized Artisans

An enterprise-grade, mobile-first web and backend ecosystem engineered to empower marginalized artisans through AI-assisted material scanning, fair-trade wage transparency, smart voice cataloging, multi-role security, dual APIs (GraphQL + REST), multi-database integration (SQLite, SQL, MongoDB), and UPI payment methods (Google Pay, PhonePe, Paytm, BHIM, Escrow).

---

## Key Highlights

- **Aesthetic Mobile UI/UX**: Designed with warm Indian heritage colors (Terracotta, Indigo, Ochre Gold, Forest Jade), dark/light themes, glassmorphism, and an interactive phone frame with notch, live clock, and bottom navigation.
- **AI Material Scanner & Retrieval**: Live camera and sample analyzer that identifies authentic materials (Banarasi Silk, Gorakhpur Terracotta, Bastar Dhokra Brass, Saharanpur Teak, Bagru Indigo Cotton, Jaipur Blue Ceramic). Instantly extracts physical properties (tensile strength, durability, GI tags), fair living wages, and assigns the nearest hyper-local green delivery courier with dispatch ETA.
- **Dual API Architecture (GraphQL + REST)**: Full Django REST Framework endpoints alongside interactive Graphene GraphQL queries & mutations.
- **Multi-Database System**: Relational models (SQLite/SQL) via Django ORM for users, transactions, orders, and products + MongoDB document store integration for deep AI spectral data & artisanal storytelling archives.
- **Role-Based Security & JWT Auth**: Dedicated portals and JWT-secured access for **Artisans**, **Clients / B2B Wholesalers / NGOs**, **Consumers**, and **Delivery Couriers**.
- **Unified Indian Payment Gateway & Escrow**: Support for UPI (**Google Pay**, **PhonePe**, **Paytm**, **BHIM**), Cards, Net Banking, and **Artisan Fair-Trade Escrow Protection** that guarantees direct payout release upon delivery.
- **Voice Accessibility for Marginalized Artisans**: Speech-to-text dictation and text-to-speech audio feedback in Hindi & English for artisans with low digital literacy.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Vanilla CSS3 (Design System tokens, glassmorphism), Modern JavaScript ES6+ |
| **Backend Framework** | Django 5.2+, Django REST Framework (DRF), Graphene-Django (GraphQL) |
| **Databases** | SQLite / SQL (Relational via Django ORM) + MongoDB (PyMongo Document Vault) |
| **Security** | JSON Web Tokens (JWT), Role-Based Access Control (RBAC), HMAC-SHA256 Escrow Seals |
| **AI Vision & Pricing** | Feature Extraction Engine, Fair Living Wage Calculator, Courier Dispatch Routing |
| **Payments** | UPI Gateway (GPay, PhonePe, Paytm, BHIM QR), Cards, Net Banking, Escrow Smart Release |

---

## Directory Structure

```
mathverse/
├── backend/
│   ├── manage.py                          # Django management CLI
│   ├── artisan_core/                      # Django project configuration
│   │   ├── settings.py                    # Settings (CORS, REST, GraphQL, DB configs)
│   │   ├── urls.py                        # Root URL routing (REST, GraphQL, Admin, Static)
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── artisans_app/                      # Core Artisan Application
│       ├── models.py                      # SQLite/SQL relational models
│       ├── mongo_service.py               # MongoDB document store layer
│       ├── ai_vision_engine.py            # AI Material recognition & fair-wage pricing
│       ├── security.py                    # JWT auth, role validation, escrow signature & sanitization
│       ├── serializers.py                 # DRF Serializers for REST API
│       ├── views.py                       # REST API Views
│       ├── schema.py                      # Graphene-Django GraphQL Schema
│       ├── urls.py                        # App-level REST endpoints
│       └── mock_seed.py                   # Initial dataset seed
├── static/
│   ├── css/
│   │   ├── design_system.css              # Rich theme tokens, gradients, animations
│   │   ├── mobile_app.css                 # Mobile app container, bottom nav, phone notch
│   │   ├── scanner.css                    # AI Camera HUD, laser animation, material cards
│   │   ├── payment_modal.css              # UPI payment sheets (GPay, PhonePe, Paytm) & Escrow
│   │   └── delivery_map.css               # Interactive live delivery tracking & courier UI
│   └── js/
│       ├── app.js                         # Core SPA routing, voice assistant, mobile frame toggles
│       ├── api_client.js                  # Unified client handling REST API & GraphQL requests
│       ├── auth_service.js                # Multi-role authentication (Artisan, Buyer, Client/NGO, Delivery)
│       ├── ai_scanner.js                  # Camera stream, material recognition & property calculator
│       ├── marketplace.js                 # Smart cataloging feed, search, filter, 3D/AR preview
│       ├── payment_gateway.js             # GPay, PhonePe, Paytm, Card & Escrow checkout
│       └── delivery_tracker.js            # Real-time courier assignment & live route tracker
├── templates/
│   └── index.html                         # Mobile application interface
├── run_server.py                          # Unified launcher
└── README.md
```

---

## How to Run the Application

Run the server with Python:

```bash
python run_server.py
```

Open your browser and navigate to:
- **Mobile Web Application**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive GraphQL Explorer (GraphiQL)**: [http://localhost:8000/graphql](http://localhost:8000/graphql)
- **REST API Base**: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **MongoDB Document Vault**: [http://localhost:8000/api/v1/mongo/vault/](http://localhost:8000/api/v1/mongo/vault/)
- **Django Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## GraphQL Examples

### 1. Scan Material & Retrieve Properties, Fair Costs, and Delivery Courier
```graphql
query {
  scanMaterial(materialHint: "BANARASI_SILK") {
    materialName
    materialCode
    category
    originRegion
    giCertified
    confidenceScore
    tensileStrength
    durabilityYears
    carbonFootprintScore
    propertiesJson
    pricing {
      rawMaterialBaseCost
      fairArtisanWage
      fairHourlyWage
      recommendedFairRetailPrice
      conventionalMiddlemanPrice
      artisanDirectSharePercent
    }
    assignedDelivery {
      name
      vehicleType
      hubCity
      rating
      estimatedDispatchMins
    }
  }
}
```

### 2. Query Marketplace Products
```graphql
query {
  allProducts(category: "Textile") {
    id
    title
    price
    fairArtisanWage
    stockQuantity
    badge
    imageUrl
  }
}
```

---

## REST API Endpoints

- `POST /api/v1/auth/login/` — Authenticate and receive JWT token.
- `POST /api/v1/auth/register/` — Register new artisan, client B2B, buyer user, or delivery courier.
- `POST /api/v1/materials/scan/` — AI Material scanning, property extraction & courier assignment.
- `GET /api/v1/materials/` — List all GI materials.
- `GET /api/v1/products/` — List active handcrafted products.
- `POST /api/v1/products/` — Create new artisan product listing.
- `POST /api/v1/payments/initiate/` — Initiate UPI payment (GPay, PhonePe, Paytm) and generate Escrow seal.
- `POST /api/v1/payments/verify/` — Verify transaction & lock funds in Escrow.
- `POST /api/v1/orders/release-escrow/` — Release escrow funds directly to artisan UPI wallet upon delivery.
- `GET /api/v1/delivery/track/<order_id>/` — Real-time GPS courier status & route milestones.
- `GET /api/v1/mongo/vault/` — Query MongoDB telemetry scans and artisan heritage archives.
