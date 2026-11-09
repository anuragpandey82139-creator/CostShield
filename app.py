import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="SAP CostShield AI",
    page_icon="🛡️",
    layout="wide"
)

DB_NAME = "costshield.db"

# ==========================================
# STYLING
# ==========================================

st.markdown("""
<style>

.stApp{
    background-color:#07111f;
    color:white;
}

section[data-testid="stSidebar"]{
    background-color:#0d1726;
}

div[data-testid="stMetric"]{
    background-color:#10243a;
    border-radius:12px;
    padding:15px;
    border:1px solid #23435f;
}

h1,h2,h3{
    color:#8dd6ff;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE
# ==========================================

def get_db():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

def init_db():

    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS risks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        traffic REAL,
        weather REAL,
        factory REAL,
        port REAL,
        geopolitical REAL,
        route REAL,
        inventory REAL,
        risk_score REAL,
        status TEXT,
        delay REAL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS suppliers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT,
        reliability REAL,
        lead_time REAL,
        cost REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================================
# RISK ENGINE
# ==========================================

def calculate_risk(data):

    score = (
        data["traffic"] * 0.24 +
        data["weather"] * 0.20 +
        (100 - data["factory"]) * 0.20 +
        data["port"] * 0.14 +
        data["geopolitical"] * 0.10 +
        data["route"] * 0.08 +
        max(0, 7 - data["inventory"]) * 0.04
    )

    score = max(0, min(score, 100))

    if score >= 70:
        status = "CRITICAL"

    elif score >= 45:
        status = "ELEVATED"

    else:
        status = "STABLE"

    delay = max(0, (score - 35) / 12)

    return {
        "risk_score": round(score, 2),
        "status": status,
        "delay": round(delay, 2)
    }

# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def save_risk(data, result):

    conn = get_db()

    conn.execute("""
    INSERT INTO risks(
        created_at,
        traffic,
        weather,
        factory,
        port,
        geopolitical,
        route,
        inventory,
        risk_score,
        status,
        delay
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, (

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        data["traffic"],
        data["weather"],
        data["factory"],
        data["port"],
        data["geopolitical"],
        data["route"],
        data["inventory"],
        result["risk_score"],
        result["status"],
        result["delay"]
    ))

    conn.commit()
    conn.close()

def get_risks():

    conn = get_db()

    df = pd.read_sql_query(
        "SELECT * FROM risks ORDER BY id DESC",
        conn
    )

    conn.close()

    return df

def save_supplier(
    name,
    location,
    reliability,
    lead_time,
    cost
):

    conn = get_db()

    conn.execute("""
    INSERT INTO suppliers(
        name,
        location,
        reliability,
        lead_time,
        cost
    )
    VALUES(?,?,?,?,?)
    """,
    (
        name,
        location,
        reliability,
        lead_time,
        cost
    ))

    conn.commit()
    conn.close()

def get_suppliers():

    conn = get_db()

    df = pd.read_sql_query(
        "SELECT * FROM suppliers",
        conn
    )

    conn.close()

    return df

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🛡️ SAP CostShield AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Risk Prediction",
        "Supplier Intelligence",
        "Alerts",
        "System"
    ]
)

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("🛡️ SAP CostShield AI")
    st.subheader("Executive Dashboard")

    risks = get_risks()
    suppliers = get_suppliers()

    total = len(risks)

    avg_risk = (
        round(
            risks["risk_score"].mean(),2
        )
        if not risks.empty
        else 0
    )

    critical = (
        len(
            risks[
                risks["status"]=="CRITICAL"
            ]
        )
        if not risks.empty
        else 0
    )

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Assessments",
        total
    )

    c2.metric(
        "Critical",
        critical
    )

    c3.metric(
        "Average Risk",
        avg_risk
    )

    c4.metric(
        "Suppliers",
        len(suppliers)
    )

    st.divider()

    if not risks.empty:

        st.subheader("Risk Trend")

        chart = risks.sort_values("id")

        st.line_chart(
            chart.set_index("id")["risk_score"]
        )

        st.dataframe(
            risks,
            use_container_width=True
        )

# ==========================================
# RISK PREDICTION
# ==========================================

elif page == "Risk Prediction":

    st.title("🤖 AI Risk Prediction")

    with st.form("risk_form"):

        c1,c2 = st.columns(2)

        with c1:

            traffic = st.slider(
                "Traffic Risk",
                0,100,20
            )

            weather = st.slider(
                "Weather Risk",
                0,100,10
            )

            factory = st.slider(
                "Factory Capacity",
                0,100,90
            )

            port = st.slider(
                "Port Risk",
                0,100,15
            )

        with c2:

            geopolitical = st.slider(
                "Geopolitical Risk",
                0,100,15
            )

            route = st.slider(
                "Route Risk",
                0,100,20
            )

            inventory = st.number_input(
                "Inventory Days",
                min_value=0.0,
                value=7.0
            )

        submit = st.form_submit_button(
            "Analyze Risk"
        )

    if submit:

        data = {

            "traffic":traffic,
            "weather":weather,
            "factory":factory,
            "port":port,
            "geopolitical":geopolitical,
            "route":route,
            "inventory":inventory
        }

        result = calculate_risk(data)

        save_risk(data,result)

        a,b,c = st.columns(3)

        a.metric(
            "Risk Score",
            result["risk_score"]
        )

        b.metric(
            "Status",
            result["status"]
        )

        c.metric(
            "Delay",
            f'{result["delay"]} hrs'
        )

        if result["status"] == "CRITICAL":
            st.error(
                "Critical risk detected"
            )

        elif result["status"] == "ELEVATED":
            st.warning(
                "Elevated risk detected"
            )

        else:
            st.success(
                "Supply chain stable"
            )

# ==========================================
# SUPPLIER
# ==========================================

elif page == "Supplier Intelligence":

    st.title("🏭 Supplier Intelligence")

    with st.form("supplier_form"):

        name = st.text_input(
            "Supplier Name"
        )

        location = st.text_input(
            "Location"
        )

        reliability = st.slider(
            "Reliability %",
            0,100,90
        )

        lead_time = st.number_input(
            "Lead Time (Days)",
            min_value=0.0
        )

        cost = st.number_input(
            "Cost",
            min_value=0.0
        )

        save = st.form_submit_button(
            "Save Supplier"
        )

    if save:

        save_supplier(
            name,
            location,
            reliability,
            lead_time,
            cost
        )

        st.success(
            "Supplier Saved"
        )

    suppliers = get_suppliers()

    if not suppliers.empty:

        st.divider()

        st.dataframe(
            suppliers,
            use_container_width=True
        )

        st.bar_chart(
            suppliers.set_index("name")[
                "reliability"
            ]
        )

# ==========================================
# ALERTS
# ==========================================

elif page == "Alerts":

    st.title("🚨 Alerts")

    risks = get_risks()

    if risks.empty:
        st.info(
            "No alerts available"
        )

    else:

        critical = risks[
            risks["status"]
            ==
            "CRITICAL"
        ]

        elevated = risks[
            risks["status"]
            ==
            "ELEVATED"
        ]

        st.metric(
            "Critical Alerts",
            len(critical)
        )

        st.metric(
            "Elevated Alerts",
            len(elevated)
        )

        if not critical.empty:

            st.error(
                "Critical Records"
            )

            st.dataframe(
                critical,
                use_container_width=True
            )

# ==========================================
# SYSTEM
# ==========================================

elif page == "System":

    st.title("⚙️ System Information")

    st.write(
        "Application : SAP CostShield AI"
    )

    st.write(
        "Framework : Streamlit"
    )

    st.write(
        "Database : SQLite"
    )

    st.write(
        "Risk Engine : Weighted AI Scoring"
    )

    risks = get_risks()
    suppliers = get_suppliers()

    st.divider()

    st.success(
        "Database Connected"
    )

    st.write(
        "Risk Records:",
        len(risks)
    )

    st.write(
        "Suppliers:",
        len(suppliers)
    )

# ==========================================
# FOOTER
# ==========================================

st.sidebar.divider()
st.sidebar.caption(
    "SAP CostShield AI v1.0"
)
