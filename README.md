# 🛡️ ReturnShield AI — Real-Time RTO & Margin Defense Engine

### **ExaThon India 2026** | **Track 02: Customers, Channels & Demand**  
### **Team: POWERHOUSE**

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Database: Exasol Personal](https://img.shields.io/badge/Exasol-In--Memory%20Columnar-FF5722.svg)](https://www.exasol.com/)
[![Framework: Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg)](https://streamlit.io/)
[![Analytics: Plotly](https://img.shields.io/badge/Plotly-5.24.1-6366F1.svg)](https://plotly.com/)

---

## 📌 Executive Summary & Problem Statement

In the Indian e-commerce and quick-commerce ecosystem, **Cash on Delivery (COD)** remains both a vital customer acquisition lever and a catastrophic source of margin erosion.

### The Indian Retail Reality
* **Dominance of COD in Bharat**: Over 55%–65% of orders across Tier 2, Tier 3, and Social Commerce channels rely on COD.
* **Return-to-Origin (RTO) Crisis**: While Quick Commerce (e.g., Blinkit, Zepto, Instamart) experiences near-zero returns (<2%) due to 10-minute turnaround and UPI dominance, apparel and footwear on D2C and marketplace channels suffer **25%–38% RTO rates**.
* **Severe Margin Destruction**:
  * Forward shipping freight: ~₹70
  * Reverse return logistics: ~₹110
  * Packaging, quality-check & restocking: ~₹40
  * Blocked inventory depreciation: ~₹30–₹50  
  👉 **Total Loss per RTO: ₹220 – ₹270**.
  
  For an order with an average ticket size of ₹1,200 and a 12% operating margin (₹144), **a single RTO wipes out the net profit of two successfully delivered orders**.

### ReturnShield AI Solution
**ReturnShield AI** is an intelligent, real-time risk interception platform powered by **Exasol's In-Memory Columnar Database** and machine learning:
1. **Dynamic RTO Risk Scoring**: Evaluates customer trust index, channel propensity, category sizing hazard, city tier, and order value in microseconds.
2. **Automated Operational Interventions**:
   * **Prepaid Incentive Discount**: Seamlessly converts high-risk COD checkouts into prepaid UPI by extending an instant ₹100 discount (costing far less than a ₹220 RTO).
   * **Interactive 2-Way WhatsApp Verification**: Validates delivery address, GPS pinpoint, and customer availability before generating shipping labels.
   * **Mandatory 2FA OTP**: Blocks bogus or duplicate impulsive orders prior to dispatch.
   * **Instant Green-Channel Priority**: Accelerates dispatch for verified, trusted customers.

---

## ⚡ Exasol In-Memory Integration & Performance Rationale

### Why Exasol for Real-Time RTO Interception?
* **Sub-Second Columnar Analytics**: Evaluating 5,000+ to 5,000,000+ transaction rows across multidimensional cohorts (channel × payment × pincode × category) requires microsecond response times during live checkout traffic.
* **High-Throughput Ingestion**: Seamlessly ingests fast-moving order streams using `pyexasol` with columnar compression and automatic indexing.
* **Zero Downtime Graceful Fallback**: ReturnShield AI includes an enterprise-grade failover mechanism. If the Exasol Personal Docker container is offline or unreachable, the system automatically transitions to a localized, vectorized analytics engine with zero user disruption.

---

## 📂 Project Directory Structure

```text
returnshield-ai/
│
├── data/
│   ├── customers.csv           # 500 synthetic Indian retail customer profiles
│   ├── products.csv            # 100 catalog items with sizing & fragility tags
│   └── orders.csv              # 5,000 enriched orders with Indian payment splits
│
├── app.py                      # Dark-mode Streamlit dashboard with interactive simulator
├── init_exasol.py              # Data generator & Exasol DB schema/table ingestion engine
├── return_risk_model.joblib    # Trained Random Forest risk scoring model
├── requirements.txt            # Locked project dependencies
├── LICENSE                     # MIT License
└── README.md                   # Comprehensive project documentation
```

---

## 🚀 Step-by-Step Setup & Run Instructions

### Prerequisites
* Python 3.10 or 3.11
* Docker (optional, for running local Exasol Personal container)

### Step 1: Clone or Navigate to the Project Directory
```bash
cd C:\Users\nithe\.gemini\antigravity\scratch\returnshield-ai
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: (Optional) Launch Exasol Personal Docker Container
To connect the live in-memory database:
```bash
docker run -d --name exasol_personal \
  -p 8563:8563 \
  --privileged \
  exasol/docker-db:latest
```
*(If Docker is not running, the platform's automatic graceful fallback will run seamlessly on local CSV datasets!)*

### Step 4: Run Data Generation & Ingestion Engine
Execute the initialization script to generate the synthetic datasets and compile the ML risk model:
```bash
python init_exasol.py
```

**Expected Initialization Output:**
```text
===========================================================================
  ReturnShield AI - Dataset Generator & Exasol Ingestion Engine  
  ExaThon India 2026 | Track 02 | Team POWERHOUSE                
===========================================================================
[INFO] Generating 500 customer records...
[INFO] Saved customers.csv: 500 records.
[INFO] Generating 100 product records...
[INFO] Saved products.csv: 100 records.
[INFO] Generating 5000 realistic orders with Indian retail payment & channel distributions...
[INFO] Saved orders.csv: 5000 records.
[INFO] Training ReturnShield Machine Learning risk model on generated orders...
[INFO] ML risk scoring model trained and saved to return_risk_model.joblib
[INFO] Probing Exasol Personal at localhost:8563...
[INFO] [GRACEFUL FALLBACK ACTIVATED] Exasol Personal container is offline.
[INFO] Local High-Performance CSV files are prepared and indexed.
[INFO] Streamlit dashboard will seamlessly run on the Local Analytics Engine.
===========================================================================
  INITIALIZATION SUMMARY  
===========================================================================
  • customers.csv        : 500 rows generated
  • products.csv         : 100 rows generated
  • orders.csv           : 5000 rows generated
  • Risk Model           : return_risk_model.joblib compiled
  • Exasol DB Status     : OFFLINE (Graceful Fallback Active, Local CSV Engine Ready)
===========================================================================
```

### Step 5: Launch the ReturnShield AI Dashboard
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## 🖥️ Platform Features & Architecture

### 1. Cyber-Defense Dark Mode Dashboard
* **Glassmorphic KPI Cards**: Live telemetry tracking Total Analyzed Orders, COD Payment Share (%), Flagged RTO Risks (%), and Cumulative Margin Saved (₹).
* **Interactive Scope Filters**: Real-time slicing by Sales Channel, Payment Method, and City Tier.

### 2. High-Impact Visual Analytics (Plotly)
* **Channel RTO Risk Distribution**: Explains the stark contrast between Quick-Commerce (<2% RTO) and Social Commerce COD (>45% RTO).
* **Mitigation Interventions Donut**: Proportions of Prepaid Discounts, WhatsApp Verifications, and Green-Channel Dispatches.
* **Payment Split vs. Hazard Index**: Visual proof of how COD drives over 80% of logistics losses.
* **Category Sizing Exposure**: Highlights Apparel & Footwear sizing risk and margin salvaged.

### 3. Real-Time Cart & Checkout Simulator
* Test any custom product, price, channel, customer tier, and payment method.
* Real-time return probability gauge powered by scikit-learn Random Forest.
* Dynamic policy prescription:
  * 🔴 **High Risk COD**: Suggests instant ₹100 prepaid UPI incentive or 2FA OTP lock.
  * 🟡 **Medium Risk**: Triggers WhatsApp location & order confirmation ping.
  * 🟢 **Low Risk**: Express green-channel dispatch.
* **What-If Experimenter**: Interactive demonstration showing that converting a customer from COD to UPI drops their return probability by ~40%!

### 4. Exasol SQL Query Inspector
* Review production-grade Exasol queries computing aggregations, cohort margins, and high-risk pincode filters.

---

## 🏆 ExaThon India 2026 Evaluation Criteria Alignment

| Evaluation Dimension | ReturnShield AI Implementation |
|---|---|
| **Exasol Core Integration** | Pyexasol connection to `localhost:8563`, schema `RETURNSHIELD`, table `ORDERS`, with automatic graceful fallback. |
| **Track 02 Relevance** | Tackles Indian retail's #1 profitability challenge: COD returns and channel friction across Quick Commerce vs D2C. |
| **Technical Depth** | Synthetic data generation + scikit-learn ML inference + Plotly interactive charts + custom dark-mode CSS. |
| **Business Value & ROI** | Directly calculates and demonstrates quantifiable margin saved (₹) via intelligent pre-dispatch interventions. |

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).  
Copyright (c) 2026 **Team POWERHOUSE — ExaThon India 2026**.
