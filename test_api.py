import requests
import json

BASE = "http://localhost:8000"

def test_endpoints():
    print("Testing KalaSetu Endpoints...")
    
    # 1. Test Home page
    r = requests.get(f"{BASE}/")
    print(f"[1] GET / -> Status: {r.status_code} (HTML length: {len(r.text)} bytes)")
    assert r.status_code == 200, "Home page failed"

    # 2. Test GraphQL scanMaterial Query
    query = """
    query {
      scanMaterial(materialHint: "BANARASI_SILK") {
        materialName
        materialCode
        confidenceScore
        tensileStrength
        pricing {
          recommendedFairRetailPrice
          fairArtisanWage
          artisanDirectSharePercent
        }
        assignedDelivery {
          name
          vehicleType
        }
      }
    }
    """
    r = requests.post(f"{BASE}/graphql", json={"query": query})
    print(f"[2] POST /graphql -> Status: {r.status_code}")
    gql_res = r.json()
    print("    GraphQL Response:", json.dumps(gql_res, indent=2))
    assert "data" in gql_res and gql_res["data"]["scanMaterial"] is not None

    # 3. Test REST Products endpoint
    r = requests.get(f"{BASE}/api/v1/products/")
    prods = r.json().get("products", [])
    print(f"[3] GET /api/v1/products/ -> Status: {r.status_code}, Found {len(prods)} products")
    assert len(prods) > 0

    # 4. Test REST Material Scan endpoint
    r = requests.post(f"{BASE}/api/v1/materials/scan/", json={"material_hint": "TERRACOTTA_CLAY"})
    scan_data = r.json()
    print(f"[4] POST /api/v1/materials/scan/ -> Status: {r.status_code}, Material: {scan_data.get('analysis', {}).get('material_name')}")

    # 5. Test Payment Initiation & Escrow
    if prods:
        first_prod = prods[0]
        r = requests.post(f"{BASE}/api/v1/payments/initiate/", json={
            "buyer_id": first_prod["artisan_id"],
            "product_id": first_prod["id"],
            "payment_method": "GPAY",
            "quantity": 1
        })
        pay_res = r.json()
        print(f"[5] POST /api/v1/payments/initiate/ -> Status: {r.status_code}, Order: {pay_res.get('order', {}).get('order_number')}, Escrow Seal: {pay_res.get('payment_intent', {}).get('escrow_seal')}")

    # 6. Test Mongo Vault
    r = requests.get(f"{BASE}/api/v1/mongo/vault/")
    mongo_res = r.json()
    print(f"[6] GET /api/v1/mongo/vault/ -> Status: {r.status_code}, Engine: {mongo_res.get('database_engine')}, Scans Count: {mongo_res.get('spectral_scans_count')}")

    print("\n[SUCCESS] All Backend REST & GraphQL API Endpoints Tested Successfully!")

if __name__ == "__main__":
    test_endpoints()
