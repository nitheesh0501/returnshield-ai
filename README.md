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
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml             # Streamlit server and dark-theme configurations
│   └── app.py                      # Dark-mode FinTech Streamlit dashboard & live simulator
│
├── backend/
│   ├── init_exasol.py              # Data generator & Exasol DB schema/table ingestion engine
│   └── return_risk_model.joblib    # Trained Random Forest risk scoring model
│
├── database/
│   ├── customers.csv               # 500 synthetic Indian retail customer profiles
│   ├── products.csv                # 100 catalog items with sizing & fragility tags
│   └── orders.csv                  # 5,000 enriched orders with Indian payment splits
│
├── .gitignore                      # Git ignore file for bytecode and temporary caches
├── requirements.txt                # Locked project dependencies
├── LICENSE                         # MIT License
└── README.md                       # Comprehensive project documentation
```

---

## 🚀 Step-by-Step Setup & Run Instructions

### Prerequisites
* Python 3.10 or 3.11
* Docker (optional, for running local Exasol Personal container)

### Step 1: Clone or Navigate to the Project Directory
```bash
cd returnshield-ai
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
*(If Docker is not running, the platform's automatic graceful fallback will run seamlessly on local CSV datasets in `database/`!)*

### Step 4: Run Data Generation & Ingestion Engine
Execute the initialization script to generate the synthetic datasets and compile the ML risk model:
```bash
python backend/init_exasol.py
```

### Step 5: Launch the ReturnShield AI Dashboard
```bash
streamlit run frontend/app.py
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
