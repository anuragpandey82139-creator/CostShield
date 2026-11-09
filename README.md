# CostShield

CostShield is a Streamlit MVP for monitoring construction and manufacturing deliveries, spotting potential delays, and exploring recovery actions before crews are left waiting or time-sensitive materials spoil.

## Run locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## MVP workflow

- **Overview:** scan inbound deliveries, delay exposure, and representative traffic, weather, and supplier-capacity signals.
- **Deliveries:** filter shipments, inspect risk factors, and simulate an alternate-route action.
- **Suppliers:** compare sample reliability and capacity, and prepare a simulated backup sourcing draft.
- **Risk lab:** adjust shipment conditions and review a transparent, illustrative delay estimate.
- **Alerts:** review and acknowledge sample delivery exceptions.

All shipment, supplier, traffic, weather, ETA, and risk values are representative demo data. The risk estimate is a weighted heuristic, not a trained machine-learning model. SAP, supplier systems, carrier routing, live environmental feeds, and email/SMS notifications are not connected; actions in the app are simulations and do not send orders or contact external services.
