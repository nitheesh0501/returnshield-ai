"""
ReturnShield AI - Dataset Generator & Exasol Ingestion Engine
ExaThon India 2026 - Track 02: Customers, Channels & Demand
Team POWERHOUSE

Generates realistic Indian retail and quick-commerce datasets:
1. customers.csv (500 rows)
2. products.csv (100 rows)
3. orders.csv (5,000 rows)

Connects to Exasol Personal via pyexasol (localhost:8563) to initialize
the RETURNSHIELD schema and ORDERS table, with a robust graceful fallback
to local CSV storage when the container is offline.
"""

import os
import sys
import time
import socket
import logging
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ReturnShield-Init")

# Set random seeds for reproducible synthetic data
np.random.seed(42)
random.seed(42)

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
DATABASE_DIR = os.path.join(REPO_ROOT, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. Indian Retail Geography & Reference Dictionaries
# ---------------------------------------------------------
INDIAN_CITIES = [
    # Tier 1 (Metros)
    {"city": "Bengaluru", "state": "Karnataka", "tier": "Tier 1", "pincodes": [560001, 560034, 560068, 560100, 560038]},
    {"city": "Mumbai", "state": "Maharashtra", "tier": "Tier 1", "pincodes": [400001, 400050, 400076, 400092, 400069]},
    {"city": "Delhi-NCR", "state": "Delhi", "tier": "Tier 1", "pincodes": [110001, 110019, 110092, 122001, 201301]},
    {"city": "Hyderabad", "state": "Telangana", "tier": "Tier 1", "pincodes": [500001, 500032, 500081, 500084, 500072]},
    {"city": "Chennai", "state": "Tamil Nadu", "tier": "Tier 1", "pincodes": [600001, 600028, 600040, 600096, 600113]},
    {"city": "Pune", "state": "Maharashtra", "tier": "Tier 1", "pincodes": [411001, 411014, 411028, 411045, 411057]},
    {"city": "Kolkata", "state": "West Bengal", "tier": "Tier 1", "pincodes": [700001, 700020, 700064, 700091, 700107]},
    # Tier 2 (Emerging Hubs)
    {"city": "Jaipur", "state": "Rajasthan", "tier": "Tier 2", "pincodes": [302001, 302015, 302020, 302033]},
    {"city": "Ahmedabad", "state": "Gujarat", "tier": "Tier 2", "pincodes": [380001, 380015, 380054, 380061]},
    {"city": "Lucknow", "state": "Uttar Pradesh", "tier": "Tier 2", "pincodes": [226001, 226010, 226016, 226024]},
    {"city": "Indore", "state": "Madhya Pradesh", "tier": "Tier 2", "pincodes": [452001, 452010, 452012]},
    {"city": "Surat", "state": "Gujarat", "tier": "Tier 2", "pincodes": [395001, 395003, 395007]},
    {"city": "Kochi", "state": "Kerala", "tier": "Tier 2", "pincodes": [682001, 682016, 682030]},
    {"city": "Chandigarh", "state": "Punjab", "tier": "Tier 2", "pincodes": [160017, 160022, 160036]},
    {"city": "Coimbatore", "state": "Tamil Nadu", "tier": "Tier 2", "pincodes": [641001, 641012, 641044]},
    # Tier 3 (High COD / High Friction Pockets)
    {"city": "Patna", "state": "Bihar", "tier": "Tier 3", "pincodes": [800001, 800014, 800020]},
    {"city": "Varanasi", "state": "Uttar Pradesh", "tier": "Tier 3", "pincodes": [221001, 221005, 221010]},
    {"city": "Agra", "state": "Uttar Pradesh", "tier": "Tier 3", "pincodes": [282001, 282004, 282007]},
    {"city": "Ranchi", "state": "Jharkhand", "tier": "Tier 3", "pincodes": [834001, 834004]},
    {"city": "Guwahati", "state": "Assam", "tier": "Tier 3", "pincodes": [781001, 781005, 781022]},
    {"city": "Bhopal", "state": "Madhya Pradesh", "tier": "Tier 3", "pincodes": [462001, 462011, 462023]},
    {"city": "Meerut", "state": "Uttar Pradesh", "tier": "Tier 3", "pincodes": [250001, 250002]},
    {"city": "Jodhpur", "state": "Rajasthan", "tier": "Tier 3", "pincodes": [342001, 342008]}
]

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Vikram", "Sneha", "Rohan", "Pooja",
    "Aditya", "Neha", "Arjun", "Kavya", "Siddharth", "Divya", "Karan", "Shreya",
    "Gaurav", "Meera", "Varun", "Rhea", "Manish", "Tanvi", "Amit", "Ishita",
    "Deepak", "Swati", "Nikhil", "Akanksha", "Suresh", "Sunita", "Harsh", "Simran"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Iyer", "Singh", "Rao", "Nair", "Mehta",
    "Reddy", "Gupta", "Chatterjee", "Mishra", "Joshi", "Bose", "Kulkarni", "Deshmukh",
    "Chopra", "Malhotra", "Saxena", "Choudhury", "Bhat", "Pillai", "Agarwal", "Bansal"
]

CATEGORIES_META = {
    "Apparel": {
        "sizing_risk": True,
        "fragile": False,
        "base_return_rate": 0.28,
        "price_range": (499, 4499),
        "sample_items": [
            "Slim Fit Cotton Kurta", "Ankle Length Denim Jeans", "Embroidered Chanderi Saree",
            "Casual Mandarin Linen Shirt", "Oversized Graphic T-Shirt", "Floral Print Maxi Dress",
            "Fleece Hooded Sweatshirt", "Formal Tapered Trousers", "Ethnic Nehru Jacket"
        ]
    },
    "Footwear": {
        "sizing_risk": True,
        "fragile": False,
        "base_return_rate": 0.22,
        "price_range": (799, 5999),
        "sample_items": [
            "Breathable Mesh Running Shoes", "Leather Penny Loafers", "Chunky Sole Sneakers",
            "Slip-on Canvas Espadrilles", "Orthopedic Cushion Slides", "Waterproof Trekking Boots"
        ]
    },
    "Electronics": {
        "sizing_risk": False,
        "fragile": True,
        "base_return_rate": 0.11,
        "price_range": (899, 14999),
        "sample_items": [
            "ANC Wireless Earbuds", "10000mAh Magnetic Power Bank", "Smart Fitness Tracker Band",
            "Mechanical Backlit Keyboard", "Fast-Charge Type-C GaN Brick", "Smart WiFi Home Security Cam"
        ]
    },
    "Beauty & Personal Care": {
        "sizing_risk": False,
        "fragile": True,
        "base_return_rate": 0.05,
        "price_range": (299, 2199),
        "sample_items": [
            "Hydrating Hyaluronic Acid Serum", "Matte Transferproof Lipstick", "Sunscreen Aqua Gel SPF 50",
            "Salicylic Acid Face Wash", "Argan Oil Hair Treatment Mask", "Vitamin C Brightening Kit"
        ]
    },
    "Home & Kitchen": {
        "sizing_risk": False,
        "fragile": True,
        "base_return_rate": 0.09,
        "price_range": (399, 3999),
        "sample_items": [
            "Tri-ply Stainless Steel Kadhai", "Borosilicate Airtight Containers", "Aromatherapy Ceramic Diffuser",
            "Memory Foam Lumbar Pillow", "100% Egyptian Cotton Bedsheet", "Kitchen Knife Set with Sheaths"
        ]
    },
    "Quick Grocery": {
        "sizing_risk": False,
        "fragile": False,
        "base_return_rate": 0.015,
        "price_range": (99, 899),
        "sample_items": [
            "Artisanal Cold Brew Coffee Cans", "Organic Cold-Pressed Coconut Oil", "Gourmet Almond Granola",
            "Greek Low-Fat Yogurt Pack", "Imported Dark Chocolate Bar", "Premium Kashmiri Walnuts"
        ]
    }
}

SALES_CHANNELS = ["Quick Commerce", "D2C Brand Store", "Marketplace", "Social Commerce"]


# ---------------------------------------------------------
# 2. Dataset Generation Functions
# ---------------------------------------------------------

def generate_customers(n=500):
    """Generate 500 synthetic Indian e-commerce customers."""
    logger.info(f"Generating {n} customer records...")
    records = []
    for i in range(1, n + 1):
        cid = f"CUST_{1000 + i}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        phone = f"+91 {random.choice([98, 97, 99, 93, 91, 88])}{random.randint(10000000, 99999999)}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@example.in"

        geo = random.choice(INDIAN_CITIES)
        city = geo["city"]
        state = geo["state"]
        tier = geo["tier"]
        pincode = random.choice(geo["pincodes"])

        account_age_days = random.randint(14, 1100)
        total_orders = max(1, int(np.random.gamma(shape=3.0, scale=3.0)))
        
        # Indian return habits vary by tier and account maturity
        if tier == "Tier 3":
            expected_return_rate = np.random.beta(a=2.0, b=5.0)  # ~28%
        elif tier == "Tier 2":
            expected_return_rate = np.random.beta(a=1.5, b=6.0)  # ~20%
        else:
            expected_return_rate = np.random.beta(a=1.2, b=7.0)  # ~14%

        prior_returns = int(np.round(total_orders * expected_return_rate))
        prior_returns = min(prior_returns, total_orders - 1) if total_orders > 1 else (1 if random.random() < 0.1 else 0)
        return_ratio = round(prior_returns / total_orders, 3)

        # Trust score (0-100)
        trust_penalty = return_ratio * 55.0
        tenure_bonus = min(20.0, (account_age_days / 365.0) * 10.0)
        volume_bonus = min(15.0, total_orders * 1.5)
        raw_trust = 75.0 - trust_penalty + tenure_bonus + volume_bonus + np.random.normal(0, 4)
        trust_score = int(np.clip(raw_trust, 25, 99))

        records.append({
            "customer_id": cid,
            "customer_name": name,
            "phone": phone,
            "email": email,
            "city": city,
            "state": state,
            "city_tier": tier,
            "delivery_pincode": pincode,
            "account_age_days": account_age_days,
            "total_historical_orders": total_orders,
            "prior_returns": prior_returns,
            "historical_return_rate": return_ratio,
            "trust_score": trust_score
        })

    df = pd.DataFrame(records)
    return df


def generate_products(n=100):
    """Generate 100 synthetic products across retail categories."""
    logger.info(f"Generating {n} product records...")
    records = []
    cat_keys = list(CATEGORIES_META.keys())

    for i in range(1, n + 1):
        pid = f"PROD_{2000 + i}"
        cat = random.choice(cat_keys)
        meta = CATEGORIES_META[cat]
        item_name = random.choice(meta["sample_items"])
        # Add modifier to make items distinct
        modifier = random.choice(["Pro", "Classic", "Premium", "Ultra", "Lite", "Daily", "Signature", "Eco", "V2"])
        full_name = f"{item_name} ({modifier})"

        price = int(random.randint(meta["price_range"][0], meta["price_range"][1]) / 10) * 10 - 1  # 499, 1299 etc
        sizing_risk = meta["sizing_risk"]
        fragile = meta["fragile"]
        cat_ret_rate = meta["base_return_rate"] + round(random.uniform(-0.02, 0.03), 3)

        records.append({
            "product_id": pid,
            "product_name": full_name,
            "category": cat,
            "price_inr": price,
            "sizing_risk_flag": sizing_risk,
            "fragile_flag": fragile,
            "avg_category_return_rate": round(cat_ret_rate, 4)
        })

    df = pd.DataFrame(records)
    return df


def generate_orders(customers_df, products_df, n=5000):
    """
    Generate 5,000 realistic orders incorporating Indian retail dynamics:
    - COD vs. UPI payment splits per tier and channel
    - Channel propensity (Quick-Commerce vs D2C vs Marketplaces vs Social)
    - Calculated risk scores and automated mitigation interventions
    - Margin saved calculation on prevented RTOs
    """
    logger.info(f"Generating {n} realistic orders with Indian retail payment & channel distributions...")
    cust_list = customers_df.to_dict(orient="records")
    prod_list = products_df.to_dict(orient="records")

    orders = []
    start_date = datetime(2026, 1, 15, 8, 0, 0)

    for i in range(1, n + 1):
        oid = f"ORD_{800000 + i}"
        cust = random.choice(cust_list)
        prod = random.choice(prod_list)

        # Channel Selection
        # Quick commerce high for grocery/beauty, D2C high for apparel, Marketplace for tech/appliances
        if prod["category"] == "Quick Grocery":
            channel = np.random.choice(
                SALES_CHANNELS,
                p=[0.75, 0.10, 0.12, 0.03]
            )
        elif prod["category"] in ["Apparel", "Footwear"]:
            channel = np.random.choice(
                SALES_CHANNELS,
                p=[0.08, 0.42, 0.35, 0.15]
            )
        else:
            channel = np.random.choice(
                SALES_CHANNELS,
                p=[0.15, 0.30, 0.45, 0.10]
            )

        # Payment Method distribution based on channel and city tier
        # Crucial Indian retail insight:
        # - Quick commerce is ~85% UPI / Cards, very low COD (<5%).
        # - Tier 3 Social Commerce / D2C can be 60-70% COD.
        tier = cust["city_tier"]
        if channel == "Quick Commerce":
            pm = np.random.choice(["UPI", "Credit/Debit Card", "COD", "Net Banking"], p=[0.78, 0.14, 0.05, 0.03])
        elif channel == "Social Commerce":
            if tier == "Tier 3":
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.72, 0.22, 0.04, 0.02])
            elif tier == "Tier 2":
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.58, 0.34, 0.06, 0.02])
            else:
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.42, 0.46, 0.10, 0.02])
        elif channel == "D2C Brand Store":
            if tier == "Tier 3":
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.60, 0.30, 0.08, 0.02])
            elif tier == "Tier 2":
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.48, 0.40, 0.10, 0.02])
            else:
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.32, 0.50, 0.15, 0.03])
        else:  # Marketplace
            if tier == "Tier 3":
                pm = np.random.choice(["COD", "UPI", "Credit/Debit Card", "Net Banking"], p=[0.45, 0.42, 0.10, 0.03])
            else:
                pm = np.random.choice(["UPI", "COD", "Credit/Debit Card", "Net Banking"], p=[0.55, 0.28, 0.14, 0.03])

        quantity = 1 if prod["category"] in ["Electronics", "Footwear"] else np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])
        delivery_fee = 0 if (prod["price_inr"] * quantity) > 999 or channel == "Quick Commerce" else 49
        order_value = int(prod["price_inr"] * quantity + delivery_fee)

        # Simulated order timestamp spread over 9 months
        order_time = start_date + timedelta(
            days=random.randint(0, 270),
            hours=random.randint(8, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # -------------------------------------------------------------
        # Indian Retail Risk Score Engine
        # -------------------------------------------------------------
        # Baseline probability from category return rate
        base_risk = prod["avg_category_return_rate"]

        # Factors:
        # 1. Payment risk: COD adds huge return-to-origin (RTO) probability
        payment_factor = 0.32 if pm == "COD" else (-0.08 if pm == "UPI" else -0.05)

        # 2. Customer Trust Score penalty/bonus
        trust_factor = (50.0 - cust["trust_score"]) / 120.0

        # 3. Channel multiplier
        channel_factor = {
            "Quick Commerce": -0.16,  # 10-minute delivery eliminates buyer's remorse
            "D2C Brand Store": 0.04,
            "Marketplace": -0.02,
            "Social Commerce": 0.14
        }[channel]

        # 4. Tier & COD Interaction (unreachable delivery / bogus orders)
        tier_cod_factor = 0.09 if (tier == "Tier 3" and pm == "COD") else (0.04 if (tier == "Tier 2" and pm == "COD") else 0.0)

        # 5. Order Value Hazard on COD (high ticket COD has severe refusal risk)
        value_hazard = 0.08 if (order_value > 3000 and pm == "COD") else 0.0

        # Composite score calculation with logistic sigmoid scaling
        linear_combination = base_risk + payment_factor + trust_factor + channel_factor + tier_cod_factor + value_hazard + np.random.normal(0, 0.04)
        raw_risk = 1.0 / (1.0 + np.exp(-4.5 * (linear_combination - 0.26)))
        risk_score = round(float(np.clip(raw_risk, 0.03, 0.97)), 4)

        is_rto_risk = bool(risk_score >= 0.50)

        # Automated Mitigation Intervention Rule Hierarchy
        if risk_score >= 0.72:
            if pm == "COD":
                intervention = "Prepaid Incentive Discount"  # Offer ₹100 instant UPI discount to switch from COD
            else:
                intervention = "Mandatory OTP Verification"
        elif 0.45 <= risk_score < 0.72:
            if pm == "COD":
                intervention = "WhatsApp Address Confirmation"
            else:
                intervention = "Automated IVR/SMS Ping"
        else:
            intervention = "Instant Green-Channel Dispatch"

        # Realistic Fulfillment Outcome:
        # Mitigated orders have significantly lower RTO
        if risk_score >= 0.72:
            # High risk
            if intervention == "Prepaid Incentive Discount":
                status = np.random.choice(
                    ["Delivered", "Returned / RTO", "Cancelled Prior Dispatch", "In Transit"],
                    p=[0.56, 0.24, 0.14, 0.06]
                )
            else:
                status = np.random.choice(
                    ["Delivered", "Returned / RTO", "Cancelled Prior Dispatch", "In Transit"],
                    p=[0.48, 0.34, 0.12, 0.06]
                )
        elif 0.45 <= risk_score < 0.72:
            status = np.random.choice(
                ["Delivered", "Returned / RTO", "Cancelled Prior Dispatch", "In Transit"],
                p=[0.76, 0.14, 0.04, 0.06]
            )
        else:
            status = np.random.choice(
                ["Delivered", "Returned / RTO", "Cancelled Prior Dispatch", "In Transit"],
                p=[0.92, 0.02, 0.01, 0.05]
            )

        # Reverse Logistics & Margin Saved Calculation
        # In India, forward shipping (~₹70) + RTO reverse shipping (~₹110) + repackaging (~₹40) = ~₹220 loss per RTO
        reverse_logistics_unit_cost = 210 if tier == "Tier 3" else 170

        # Margin saved occurs when high-risk orders were successfully delivered or cancelled before dispatch
        if is_rto_risk and status in ["Delivered", "Cancelled Prior Dispatch"]:
            # Delivery fee + reverse freight saved
            margin_saved = int(reverse_logistics_unit_cost + (order_value * 0.05))
        else:
            margin_saved = 0

        orders.append({
            "order_id": oid,
            "customer_id": cust["customer_id"],
            "product_id": prod["product_id"],
            "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "channel": channel,
            "payment_method": pm,
            "quantity": quantity,
            "unit_price_inr": prod["price_inr"],
            "order_value_inr": order_value,
            "product_category": prod["category"],
            "delivery_city": cust["city"],
            "city_tier": cust["city_tier"],
            "delivery_pincode": cust["delivery_pincode"],
            "sizing_risk": prod["sizing_risk_flag"],
            "customer_trust_score": cust["trust_score"],
            "customer_return_ratio": cust["historical_return_rate"],
            "risk_score": risk_score,
            "is_rto_risk": is_rto_risk,
            "intervention_type": intervention,
            "order_status": status,
            "margin_saved_inr": margin_saved
        })

    df = pd.DataFrame(orders)
    return df


def train_and_export_ml_model(orders_df):
    """
    Train a fast Random Forest classifier to power the Live Order Simulator in app.py.
    Predicts return risk probability in microseconds.
    """
    logger.info("Training ReturnShield Machine Learning risk model on generated orders...")
    
    # Feature engineering
    feature_df = pd.DataFrame({
        "order_value_inr": orders_df["order_value_inr"],
        "unit_price_inr": orders_df["unit_price_inr"],
        "quantity": orders_df["quantity"],
        "is_cod": (orders_df["payment_method"] == "COD").astype(int),
        "is_upi": (orders_df["payment_method"] == "UPI").astype(int),
        "is_quick_commerce": (orders_df["channel"] == "Quick Commerce").astype(int),
        "is_d2c": (orders_df["channel"] == "D2C Brand Store").astype(int),
        "is_marketplace": (orders_df["channel"] == "Marketplace").astype(int),
        "is_social_commerce": (orders_df["channel"] == "Social Commerce").astype(int),
        "sizing_risk": orders_df["sizing_risk"].astype(int),
        "trust_score": orders_df["customer_trust_score"],
        "customer_return_ratio": orders_df["customer_return_ratio"],
        "tier_1": (orders_df["city_tier"] == "Tier 1").astype(int),
        "tier_2": (orders_df["city_tier"] == "Tier 2").astype(int),
        "tier_3": (orders_df["city_tier"] == "Tier 3").astype(int)
    })
    
    y = orders_df["is_rto_risk"].astype(int)

    clf = RandomForestClassifier(n_estimators=60, max_depth=8, random_state=42, n_jobs=-1)
    clf.fit(feature_df, y)

    model_path = os.path.join(BASE_DIR, "return_risk_model.joblib")
    joblib.dump(clf, model_path)
    logger.info(f"ML risk scoring model trained and saved to {model_path}")
    return clf


# ---------------------------------------------------------
# 3. Exasol Connection & Fallback Engine
# ---------------------------------------------------------

def is_port_open(host, port, timeout=2.0):
    """Check if the target host and port are listening before connecting."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def setup_exasol_or_fallback(orders_df, customers_df, products_df):
    """
    Connects to Exasol Personal via pyexasol (localhost:8563).
    Creates schema RETURNSHIELD and table ORDERS.
    If the Exasol container is offline or unreachable, provides a smooth,
    informative graceful fallback to local CSVs.
    """
    exasol_host = os.environ.get("EXASOL_HOST", "localhost")
    exasol_port = int(os.environ.get("EXASOL_PORT", 8563))
    exasol_user = os.environ.get("EXASOL_USER", "sys")
    exasol_password = os.environ.get("EXASOL_PASSWORD", "exasol")
    exasol_schema = os.environ.get("EXASOL_SCHEMA", "RETURNSHIELD")

    logger.info(f"Probing Exasol Personal at {exasol_host}:{exasol_port}...")

    # Fast port connectivity test to prevent long socket lockups
    if not is_port_open(exasol_host, exasol_port, timeout=2.0):
        logger.warning(f"Exasol port {exasol_host}:{exasol_port} is not reachable.")
        logger.info("=" * 70)
        logger.info("[GRACEFUL FALLBACK ACTIVATED] Exasol Personal container is offline.")
        logger.info("Local High-Performance CSV files are prepared and indexed.")
        logger.info("Streamlit dashboard will seamlessly run on the Local Analytics Engine.")
        logger.info("=" * 70)
        return False

    try:
        import pyexasol
        logger.info(f"Connecting to Exasol Personal ({exasol_host}:{exasol_port}) as user '{exasol_user}'...")
        C = pyexasol.connect(
            dsn=f"{exasol_host}:{exasol_port}",
            user=exasol_user,
            password=exasol_password,
            encryption=False,
            connection_timeout=5
        )

        logger.info(f"Connected to Exasol version: {C.meta.db_version}")

        # Create Schema
        logger.info(f"Creating schema '{exasol_schema}'...")
        C.execute(f"CREATE SCHEMA IF NOT EXISTS {exasol_schema}")
        C.execute(f"OPEN SCHEMA {exasol_schema}")

        # Create Table ORDERS
        logger.info("Creating table 'ORDERS'...")
        create_table_sql = """
        CREATE OR REPLACE TABLE ORDERS (
            order_id VARCHAR(32) PRIMARY KEY,
            customer_id VARCHAR(32),
            product_id VARCHAR(32),
            order_timestamp TIMESTAMP,
            channel VARCHAR(64),
            payment_method VARCHAR(64),
            quantity DECIMAL(9,0),
            unit_price_inr DECIMAL(12,2),
            order_value_inr DECIMAL(12,2),
            product_category VARCHAR(64),
            delivery_city VARCHAR(64),
            city_tier VARCHAR(16),
            delivery_pincode DECIMAL(9,0),
            sizing_risk BOOLEAN,
            customer_trust_score DECIMAL(5,0),
            customer_return_ratio DOUBLE PRECISION,
            risk_score DOUBLE PRECISION,
            is_rto_risk BOOLEAN,
            intervention_type VARCHAR(64),
            order_status VARCHAR(64),
            margin_saved_inr DECIMAL(12,2)
        )
        """
        C.execute(create_table_sql)

        # Ingest orders dataframe
        logger.info(f"Ingesting {len(orders_df)} rows into Exasol table RETURNSHIELD.ORDERS...")
        C.import_from_pandas(orders_df, "ORDERS")

        # Verify row count
        count_res = C.execute("SELECT COUNT(*) FROM ORDERS").fetchall()
        logger.info(f"Verification successful: {count_res[0][0]} rows stored in RETURNSHIELD.ORDERS!")

        C.close()
        logger.info("Exasol ingestion completed successfully.")
        return True

    except Exception as e:
        logger.warning(f"Exasol connection or query error: {e}")
        logger.info("=" * 70)
        logger.info("[GRACEFUL FALLBACK ACTIVATED] Proceeding with local dataset storage.")
        logger.info("=" * 70)
        return False


def main():
    print("=" * 75)
    print("  ReturnShield AI - Dataset Generator & Exasol Ingestion Engine  ")
    print("  ExaThon India 2026 | Track 02 | Team POWERHOUSE                ")
    print("=" * 75)

    # 1. Generate Customers
    customers_df = generate_customers(n=500)
    customers_csv_path = os.path.join(DATABASE_DIR, "customers.csv")
    customers_df.to_csv(customers_csv_path, index=False)
    logger.info(f"Saved customers.csv: {len(customers_df)} records to {customers_csv_path}.")

    # 2. Generate Products
    products_df = generate_products(n=100)
    products_csv_path = os.path.join(DATABASE_DIR, "products.csv")
    products_df.to_csv(products_csv_path, index=False)
    logger.info(f"Saved products.csv: {len(products_df)} records to {products_csv_path}.")

    # 3. Generate Orders
    orders_df = generate_orders(customers_df, products_df, n=5000)
    orders_csv_path = os.path.join(DATABASE_DIR, "orders.csv")
    orders_df.to_csv(orders_csv_path, index=False)
    logger.info(f"Saved orders.csv: {len(orders_df)} records to {orders_csv_path}.")

    # 4. Train Risk Model for Fast Interactive Simulator
    train_and_export_ml_model(orders_df)

    # 5. Connect to Exasol Personal or activate Graceful Fallback
    exasol_ready = setup_exasol_or_fallback(orders_df, customers_df, products_df)

    print("\n" + "=" * 75)
    print("  INITIALIZATION SUMMARY  ")
    print("=" * 75)
    print(f"  • customers.csv        : {len(customers_df)} rows generated")
    print(f"  • products.csv         : {len(products_df)} rows generated")
    print(f"  • orders.csv           : {len(orders_df)} rows generated")
    print(f"  • Risk Model           : return_risk_model.joblib compiled")
    if exasol_ready:
        print(f"  • Exasol DB Status     : CONNECTED (Table RETURNSHIELD.ORDERS loaded)")
    else:
        print(f"  • Exasol DB Status     : OFFLINE (Graceful Fallback Active, Local CSV Engine Ready)")
    print("=" * 75)


if __name__ == "__main__":
    main()
