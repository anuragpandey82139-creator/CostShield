from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="CostShield | Supply control tower",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAV_ITEMS = [
    "Overview",
    "Deliveries",
    "Suppliers",
    "Risk lab",
    "Alerts",
]

SHIPMENTS = [
    {
        "id": "CS-2841",
        "material": "Ready-mix concrete",
        "project": "North Tower · Zone B",
        "supplier": "Apex Concrete",
        "origin": "Newark, NJ",
        "eta": "09:40",
        "quantity": "42 yd³",
        "value": 18400,
        "traffic": 92,
        "weather": 43,
        "capacity": 76,
        "inventory": 0.4,
        "route": "I-78 · 18 mi",
        "latitude": 40.76,
        "longitude": -74.16,
    },
    {
        "id": "CS-2838",
        "material": "Rebar · Grade 60",
        "project": "Harbor Works · Pier 4",
        "supplier": "Metro Steel Co.",
        "origin": "Edison, NJ",
        "eta": "10:15",
        "quantity": "18 tons",
        "value": 31200,
        "traffic": 71,
        "weather": 18,
        "capacity": 88,
        "inventory": 1.8,
        "route": "NJ Turnpike · 24 mi",
        "latitude": 40.54,
        "longitude": -74.37,
    },
    {
        "id": "CS-2844",
        "material": "Structural steel",
        "project": "North Tower · Zone A",
        "supplier": "Metro Steel Co.",
        "origin": "Edison, NJ",
        "eta": "11:30",
        "quantity": "12 tons",
        "value": 26800,
        "traffic": 35,
        "weather": 12,
        "capacity": 91,
        "inventory": 3.2,
        "route": "US-1 · 26 mi",
        "latitude": 40.69,
        "longitude": -74.22,
    },
    {
        "id": "CS-2846",
        "material": "Ready-mix concrete",
        "project": "Riverside Plant · Pour 2",
        "supplier": "Riverbend Materials",
        "origin": "Elizabeth, NJ",
        "eta": "12:05",
        "quantity": "28 yd³",
        "value": 12600,
        "traffic": 58,
        "weather": 66,
        "capacity": 64,
        "inventory": 1.1,
        "route": "I-95 · 14 mi",
        "latitude": 40.67,
        "longitude": -74.19,
    },
    {
        "id": "CS-2849",
        "material": "Electrical conduit",
        "project": "Harbor Works · Core",
        "supplier": "Hudson Industrial",
        "origin": "Jersey City, NJ",
        "eta": "13:20",
        "quantity": "240 units",
        "value": 8400,
        "traffic": 24,
        "weather": 8,
        "capacity": 96,
        "inventory": 5.0,
        "route": "Local delivery · 6 mi",
        "latitude": 40.73,
        "longitude": -74.08,
    },
]

SUPPLIERS = [
    {
        "name": "Apex Concrete",
        "location": "Newark, NJ",
        "reliability": 96,
        "capacity": 76,
        "lead_time": "2.4 hrs",
        "status": "Capacity tight",
    },
    {
        "name": "Metro Steel Co.",
        "location": "Edison, NJ",
        "reliability": 98,
        "capacity": 88,
        "lead_time": "1.8 days",
        "status": "On schedule",
    },
    {
        "name": "Riverbend Materials",
        "location": "Elizabeth, NJ",
        "reliability": 91,
        "capacity": 64,
        "lead_time": "3.1 hrs",
        "status": "Weather watch",
    },
    {
        "name": "Hudson Industrial",
        "location": "Jersey City, NJ",
        "reliability": 99,
        "capacity": 96,
        "lead_time": "4.2 hrs",
        "status": "On schedule",
    },
]

st.markdown(
    """
    <style>
    :root {
        --ink: #e8eef5;
        --muted: #8292a5;
        --panel: #111b27;
        --line: #223141;
        --mint: #65e0b1;
    }
    .stApp { background: #0a111a; color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(10,17,26,.88); }
    [data-testid="stSidebar"] { background: #0d1620; border-right: 1px solid #1d2b39; }
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; letter-spacing: -.035em; }
    h1 { font-size: 2rem !important; color: #f0f5fa; }
    h2 { font-size: 1.25rem !important; color: #edf3f8; }
    h3 { font-size: 1.02rem !important; color: #edf3f8; }
    p, label, [data-testid="stMarkdownContainer"] { color: #c0cad5; }
    [data-testid="stMetric"] {
        background: #111b27; border: 1px solid #223141; border-radius: 12px;
        padding: 16px 18px; min-height: 112px;
    }
    [data-testid="stMetricLabel"] { color: #91a1b3; font-size: .82rem; }
    [data-testid="stMetricValue"] { color: #f1f5f9; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stMetricDelta"] { font-size: .76rem; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #111b27; border-color: #223141 !important; border-radius: 12px;
    }
    [data-testid="stDataFrame"] { border: 1px solid #223141; border-radius: 10px; }
    .eyebrow {
        color: #7f91a5; font-size: .72rem; font-weight: 700;
        letter-spacing: .12em; text-transform: uppercase;
    }
    .page-subtitle { color: #8d9daf; margin-top: -.65rem; }
    .live-pill {
        display: inline-block; padding: 5px 10px; border-radius: 20px;
        color: #73e5b7; background: #103328; font-size: .75rem; font-weight: 600;
    }
    .risk-critical { color: #ff8c83; font-weight: 700; }
    .risk-elevated { color: #f5c46b; font-weight: 700; }
    .risk-stable { color: #76dfb1; font-weight: 700; }
    .stButton > button[kind="primary"] {
        background: #38c995; border: 0; color: #062116; font-weight: 700;
    }
    .stButton > button[kind="primary"]:hover {
        background: #67dfb2; border: 0; color: #062116;
    }
    div[data-testid="stTabs"] button { color: #9cabbc; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def assess_delay(shipment):
    """Return an illustrative risk estimate from the demo condition signals."""
    inventory_pressure = max(0, min(100, (3 - shipment["inventory"]) * 32))
    score = (
        shipment["traffic"] * 0.34
        + shipment["weather"] * 0.23
        + (100 - shipment["capacity"]) * 0.23
        + inventory_pressure * 0.20
    )
    probability = max(4, min(96, round(15 + score * 0.9)))
    delay_hours = max(0, round((score - 27) / 9, 1))
    if probability >= 70:
        status = "Critical"
    elif probability >= 42:
        status = "Watch"
    else:
        status = "On track"
    return {
        "risk_score": round(score),
        "probability": probability,
        "delay_hours": delay_hours,
        "status": status,
    }


def get_shipments():
    shipments = []
    rerouted = st.session_state.get("rerouted_shipments", set())
    for shipment in SHIPMENTS:
        item = shipment.copy()
        item.update(assess_delay(item))
        if item["id"] in rerouted:
            item["route"] = "Alternate · US-22"
            item["probability"] = max(8, item["probability"] - 30)
            item["delay_hours"] = 0.4
            item["status"] = "Rerouted"
        shipments.append(item)
    return shipments


def money(value):
    return f"${value:,.0f}"


def chart_layout(fig, height=280):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aab7c5", family="DM Sans"),
        xaxis=dict(gridcolor="#223141", zerolinecolor="#223141"),
        yaxis=dict(gridcolor="#223141", zerolinecolor="#223141"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12),
    )
    return fig


def shipment_table(shipments):
    frame = pd.DataFrame(shipments)
    display = frame[
        [
            "id",
            "material",
            "project",
            "supplier",
            "eta",
            "probability",
            "delay_hours",
            "status",
        ]
    ].rename(
        columns={
            "id": "Shipment",
            "material": "Material",
            "project": "Project",
            "supplier": "Supplier",
            "eta": "ETA",
            "probability": "Delay risk",
            "delay_hours": "Est. delay (h)",
            "status": "Status",
        }
    )
    return display


def page_header(title, subtitle, icon):
    st.markdown(f"<div class='eyebrow'>{icon} &nbsp; COSTSHIELD CONTROL TOWER</div>", unsafe_allow_html=True)
    st.title(title)
    st.markdown(f"<p class='page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def render_overview(shipments):
    now = datetime.now().strftime("%H:%M")
    critical_count = sum(item["status"] == "Critical" for item in shipments)
    exposed_value = sum(
        item["value"] for item in shipments if item["status"] in ("Critical", "Watch")
    )
    delayed_hours = sum(item["delay_hours"] for item in shipments)

    left, right = st.columns([0.75, 0.25])
    with left:
        page_header(
            "Supply, before it slips.",
            "A live-style view of material movement across your active projects.",
            "◈",
        )
    with right:
        st.markdown(
            "<div style='text-align:right;padding-top:12px'>"
            "<span class='live-pill'>● DEMO MONITORING</span>"
            f"<div style='color:#8190a1;font-size:.78rem;margin-top:8px'>Snapshot · {now}</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inbound shipments", len(shipments), "Across 3 active projects")
    m2.metric("At-risk deliveries", critical_count + sum(s["status"] == "Watch" for s in shipments), f"{critical_count} critical")
    m3.metric("Delay exposure", f"{delayed_hours:.1f} hrs", "Estimated across inbound")
    m4.metric("Materials exposed", money(exposed_value), "Value of watch + critical loads")

    st.write("")
    chart_col, signal_col = st.columns([1.55, 1])
    with chart_col:
        with st.container(border=True):
            st.markdown("#### Delivery risk outlook")
            st.caption("Estimated delay probability for today's inbound loads")
            data = pd.DataFrame(shipments).sort_values("eta")
            colors = [
                "#f07870" if status == "Critical"
                else "#efbd64" if status == "Watch"
                else "#59cfa0"
                for status in data["status"]
            ]
            fig = go.Figure(
                go.Bar(
                    x=data["probability"],
                    y=data["id"] + " · " + data["material"],
                    orientation="h",
                    marker_color=colors,
                    text=data["probability"].astype(str) + "%",
                    textposition="outside",
                    cliponaxis=False,
                )
            )
            fig.update_xaxes(range=[0, 110], title="Delay probability", ticksuffix="%")
            fig.update_yaxes(autorange="reversed", title=None)
            st.plotly_chart(chart_layout(fig, 255), use_container_width=True, config={"displayModeBar": False})

    with signal_col:
        with st.container(border=True):
            st.markdown("#### Environment watch")
            st.caption("Representative local signals · demo feed")
            conditions = [
                ("🚦", "Traffic · I-78 West", "Heavy · 18 min added", 76, "#efbd64"),
                ("🌧️", "Weather · Newark", "Showers after 10:00", 43, "#6bb6e8"),
                ("🏭", "Apex Concrete capacity", "76% available", 76, "#efbd64"),
                ("🏭", "Metro Steel capacity", "88% available", 88, "#59cfa0"),
            ]
            for icon, label, detail, value, color in conditions:
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;margin:15px 0 5px'>"
                    f"<span style='color:#e2e9f0'>{icon} &nbsp; {label}</span>"
                    f"<span style='color:#8999aa'>{detail}</span></div>"
                    f"<div style='height:5px;border-radius:4px;background:#1f2c39'>"
                    f"<div style='height:5px;width:{value}%;border-radius:4px;background:{color}'></div></div>",
                    unsafe_allow_html=True,
                )
            st.caption("Signals are sample values and are not connected to external feeds.")

    st.write("")
    with st.container(border=True):
        title_col, action_col = st.columns([0.8, 0.2])
        title_col.markdown("#### Deliveries that need a decision")
        title_col.caption("Prioritized by estimated delay probability")
        if action_col.button("Open delivery board →", key="overview_deliveries"):
            st.session_state["navigation"] = "Deliveries"
            st.rerun()
        st.dataframe(
            shipment_table(sorted(shipments, key=lambda item: item["probability"], reverse=True)),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Delay risk": st.column_config.ProgressColumn(
                    "Delay risk", min_value=0, max_value=100, format="%d%%"
                ),
                "Status": st.column_config.TextColumn("Status"),
            },
        )

    critical = [item for item in shipments if item["status"] == "Critical"]
    if critical:
        first = critical[0]
        st.warning(
            f"**Action suggested · {first['id']}** — {first['material']} for {first['project']} "
            f"has an estimated {first['probability']}% delay risk. Review an alternate route or supplier."
        )


def render_deliveries(shipments):
    page_header(
        "Inbound deliveries",
        "Review expected arrivals, risk factors, and available recovery actions.",
        "↗",
    )
    selected_status = st.selectbox("Filter deliveries", ["All", "Critical", "Watch", "On track", "Rerouted"])
    filtered = shipments if selected_status == "All" else [s for s in shipments if s["status"] == selected_status]
    st.dataframe(
        shipment_table(filtered),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Delay risk": st.column_config.ProgressColumn(
                "Delay risk", min_value=0, max_value=100, format="%d%%"
            ),
        },
    )

    st.write("")
    with st.container(border=True):
        st.markdown("#### Recovery actions")
        delivery_id = st.selectbox(
            "Choose a shipment",
            [item["id"] for item in shipments],
            format_func=lambda shipment_id: next(
                f"{item['id']} · {item['material']} — {item['project']}"
                for item in shipments if item["id"] == shipment_id
            ),
        )
        selected = next(item for item in shipments if item["id"] == delivery_id)
        details, conditions = st.columns([1, 1])
        details.write(f"**Supplier:** {selected['supplier']}  ·  **ETA:** {selected['eta']}")
        details.write(f"**Route:** {selected['route']}  ·  **Load:** {selected['quantity']}")
        conditions.write(f"**Delay probability:** {selected['probability']}%  ·  **Est. delay:** {selected['delay_hours']} hrs")
        conditions.write(f"**Traffic:** {selected['traffic']} / 100  ·  **Supplier capacity:** {selected['capacity']}%")
        rerouted = delivery_id in st.session_state.get("rerouted_shipments", set())
        button_label = "Route already adjusted" if rerouted else "Calculate alternate route"
        if st.button(button_label, type="primary", disabled=rerouted, key=f"route_{delivery_id}"):
            updated = set(st.session_state.get("rerouted_shipments", set()))
            updated.add(delivery_id)
            st.session_state["rerouted_shipments"] = updated
            st.session_state["last_action"] = f"Alternate route selected for {delivery_id}"
            st.rerun()
        if st.session_state.get("last_action", "").endswith(delivery_id):
            st.success(
                f"{st.session_state['last_action']}. The demo estimate is updated; no carrier or SAP system was contacted."
            )

    with st.container(border=True):
        st.markdown("#### Route context")
        st.caption("Sample supplier and route origin locations — illustrative only, not a live GPS feed.")
        map_data = pd.DataFrame(shipments)[["latitude", "longitude"]]
        st.map(map_data, latitude="latitude", longitude="longitude", size=80, color="#59cfa0", use_container_width=True)


def render_suppliers():
    page_header(
        "Supplier intelligence",
        "Capacity and reliability signals help surface a feasible backup before a site runs short.",
        "⌂",
    )
    suppliers = pd.DataFrame(SUPPLIERS)
    avg_reliability = round(suppliers["reliability"].mean())
    low_capacity = int((suppliers["capacity"] < 70).sum())
    a, b, c = st.columns(3)
    a.metric("Active suppliers", len(suppliers), "Demo directory")
    b.metric("Average reliability", f"{avg_reliability}%", "Historical sample")
    c.metric("Capacity constrained", low_capacity, "Below 70% available")
    st.write("")
    left, right = st.columns([1.1, 0.9])
    with left:
        with st.container(border=True):
            st.markdown("#### Supplier capacity")
            fig = px.bar(
                suppliers.sort_values("capacity"),
                x="capacity",
                y="name",
                orientation="h",
                color="capacity",
                color_continuous_scale=["#efbd64", "#59cfa0"],
                range_color=[0, 100],
                text="capacity",
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside", showlegend=False)
            fig.update_xaxes(range=[0, 112], title="Available capacity", ticksuffix="%")
            fig.update_yaxes(title=None)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(chart_layout(fig, 260), use_container_width=True, config={"displayModeBar": False})
    with right:
        with st.container(border=True):
            st.markdown("#### Backup options")
            st.caption("Sample supplier directory · confirm before placing a real order")
            for supplier in SUPPLIERS:
                status_color = "#f0bf68" if supplier["capacity"] < 70 else "#70ddb0"
                st.markdown(
                    f"<div style='padding:11px 0;border-bottom:1px solid #223141'>"
                    f"<div style='display:flex;justify-content:space-between'>"
                    f"<strong style='color:#e7edf4'>{supplier['name']}</strong>"
                    f"<span style='color:{status_color};font-size:.8rem'>{supplier['status']}</span></div>"
                    f"<div style='color:#8595a7;font-size:.82rem;margin-top:5px'>"
                    f"{supplier['location']} · {supplier['capacity']}% capacity · "
                    f"{supplier['reliability']}% reliability · {supplier['lead_time']} lead</div></div>",
                    unsafe_allow_html=True,
                )
    st.info("Capacity, lead time, and reliability are representative sample data; supplier systems are not connected.")

    with st.container(border=True):
        st.markdown("#### Draft a backup sourcing action")
        eligible = [supplier["name"] for supplier in SUPPLIERS if supplier["capacity"] >= 70]
        order_col, supplier_col, qty_col, action_col = st.columns([1.1, 1.1, 0.7, 0.9])
        material = order_col.selectbox("Material", ["Ready-mix concrete", "Rebar · Grade 60", "Structural steel"])
        backup = supplier_col.selectbox("Backup supplier", eligible)
        quantity = qty_col.number_input("Quantity", min_value=1, value=1, step=1)
        if action_col.button("Prepare order", type="primary"):
            st.session_state["backup_order"] = {
                "material": material,
                "supplier": backup,
                "quantity": quantity,
            }
    if st.session_state.get("backup_order"):
        order = st.session_state["backup_order"]
        st.success(
            f"Demo draft prepared: {order['quantity']} unit(s) of {order['material']} from {order['supplier']}. "
            "No purchase order was sent to SAP."
        )


def render_risk_lab():
    page_header(
        "Risk lab",
        "Explore how changing field conditions may change an inbound shipment's delay outlook.",
        "⌁",
    )
    st.info("Demo estimate only — an illustrative weighted scoring model, not a trained ML prediction or live feed.")
    shipment_id = st.selectbox(
        "Baseline shipment",
        [item["id"] for item in SHIPMENTS],
        format_func=lambda shipment_id: next(
            f"{item['id']} · {item['material']} — {item['project']}"
            for item in SHIPMENTS if item["id"] == shipment_id
        ),
    )
    base = next(item for item in SHIPMENTS if item["id"] == shipment_id)
    controls, result = st.columns([1, 1])
    with controls:
        with st.container(border=True):
            st.markdown("#### Adjust conditions")
            traffic = st.slider("Traffic disruption", 0, 100, int(base["traffic"]))
            weather = st.slider("Severe weather", 0, 100, int(base["weather"]))
            capacity = st.slider("Supplier capacity", 0, 100, int(base["capacity"]))
            inventory = st.slider("Inventory cover (days)", 0.0, 7.0, float(base["inventory"]), 0.1)
    simulated = base.copy()
    simulated.update(traffic=traffic, weather=weather, capacity=capacity, inventory=inventory)
    estimate = assess_delay(simulated)
    with result:
        with st.container(border=True):
            st.markdown("#### Illustrative estimate")
            a, b = st.columns(2)
            a.metric("Delay probability", f"{estimate['probability']}%")
            b.metric("Expected delay", f"{estimate['delay_hours']} hrs")
            st.progress(estimate["probability"] / 100)
            st.markdown(f"**Risk band:** {estimate['status']}")
            st.caption("Score weights: traffic 34% · weather 23% · supplier capacity 23% · inventory pressure 20%.")
            if estimate["status"] == "Critical":
                st.error("Consider a route alternative or checking qualified backup supply.")
            elif estimate["status"] == "Watch":
                st.warning("Monitor conditions and confirm the supplier's next dispatch window.")
            else:
                st.success("No immediate recovery action suggested by this demo estimate.")

    with st.container(border=True):
        st.markdown("#### Assessment history")
        if "assessments" not in st.session_state:
            st.session_state["assessments"] = []
        if st.button("Save this assessment"):
            st.session_state["assessments"].insert(
                0,
                {
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Shipment": shipment_id,
                    "Risk": f"{estimate['probability']}%",
                    "Est. delay": f"{estimate['delay_hours']} hrs",
                    "Band": estimate["status"],
                },
            )
        if st.session_state["assessments"]:
            st.dataframe(pd.DataFrame(st.session_state["assessments"]), hide_index=True, use_container_width=True)
        else:
            st.caption("Saved assessments will appear here for this session.")


def render_alerts(shipments):
    page_header(
        "Alert center",
        "Prioritized delivery exceptions and suggested next steps for project teams.",
        "⚑",
    )
    alert_rows = sorted(
        [item for item in shipments if item["status"] in ("Critical", "Watch")],
        key=lambda item: item["probability"],
        reverse=True,
    )
    critical_count = sum(item["status"] == "Critical" for item in alert_rows)
    a, b, c = st.columns(3)
    a.metric("Open alerts", len(alert_rows), "Generated from demo signals")
    b.metric("Critical", critical_count, "Immediate review recommended")
    c.metric("Watch", len(alert_rows) - critical_count, "Continue monitoring")
    st.write("")
    if not alert_rows:
        st.success("No demo shipment alerts at the moment.")
    for item in alert_rows:
        with st.container(border=True):
            left, right = st.columns([0.76, 0.24])
            with left:
                status_icon = "🔴" if item["status"] == "Critical" else "🟠"
                st.markdown(f"**{status_icon} {item['status']} · {item['id']} — {item['material']}**")
                st.caption(
                    f"{item['project']} · {item['supplier']} · ETA {item['eta']} · "
                    f"{item['probability']}% estimated delay probability"
                )
                if item["material"] == "Ready-mix concrete":
                    st.write("Time-sensitive load: confirm dispatch window to reduce spoilage and crew idle time.")
                elif item["weather"] >= 50:
                    st.write("Weather signal is elevated: verify the supplier's production and dispatch plan.")
                else:
                    st.write("Check the carrier's route and confirm the latest arrival window with the site.")
            with right:
                st.metric("Est. delay", f"{item['delay_hours']} hrs")
                is_acknowledged = item["id"] in st.session_state.get("acknowledged_alerts", set())
                if st.button(
                    "Acknowledged" if is_acknowledged else "Acknowledge",
                    key=f"ack_{item['id']}",
                    disabled=is_acknowledged,
                ):
                    acknowledged = set(st.session_state.get("acknowledged_alerts", set()))
                    acknowledged.add(item["id"])
                    st.session_state["acknowledged_alerts"] = acknowledged
                    st.rerun()
                if is_acknowledged:
                    st.caption("Acknowledged in this demo session")
    st.caption("Alerts are generated from sample shipment data. No email, SMS, or external notification is sent.")


with st.sidebar:
    st.markdown(
        "<div style='padding:8px 0 20px'>"
        "<div style='font-family:Segoe UI;font-size:1.25rem;color:#eff5fa;font-weight:700'>"
        "🛡️ CostShield</div>"
        "<div style='color:#8090a2;font-size:.78rem;margin-top:3px'>SUPPLY CONTROL TOWER</div></div>",
        unsafe_allow_html=True,
    )
    if "navigation" not in st.session_state:
        st.session_state["navigation"] = "Overview"
    page = st.radio("WORKSPACE", NAV_ITEMS, key="navigation", label_visibility="visible")
    st.divider()
    st.markdown("**Today · Newark region**")
    st.caption("3 projects · 5 inbound loads")
    st.markdown("<span class='live-pill'>● DEMO DATA</span>", unsafe_allow_html=True)
    st.divider()
    st.caption("Connectors not configured")
    st.caption("SAP · Traffic · Weather")


shipments = get_shipments()
if page == "Overview":
    render_overview(shipments)
elif page == "Deliveries":
    render_deliveries(shipments)
elif page == "Suppliers":
    render_suppliers()
elif page == "Risk lab":
    render_risk_lab()
elif page == "Alerts":
    render_alerts(shipments)

st.markdown(
    "<div style='padding:25px 0 4px;color:#647487;font-size:.74rem;border-top:1px solid #1d2b39'>"
    "COSTSHIELD MVP · SAMPLE OPERATIONS DATA · NO LIVE SUPPLIER, CARRIER, WEATHER, OR SAP CONNECTION</div>",
    unsafe_allow_html=True,
)
