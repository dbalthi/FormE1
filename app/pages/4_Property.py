import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app._bootstrap import load_cfg
from core.property.calculators import coerce_airbnb, monthly_summary, occupancy_heatmap
from core.export.charts import save_plotly_figure

st.set_page_config(page_title="Property & Airbnb", page_icon="🏠", layout="wide")

cfg, APP_ROOT = load_cfg()
parsed_dir  = (APP_ROOT / cfg["data"]["parsed_dir"]).resolve()
charts_dir  = (APP_ROOT / cfg["artifacts"]["charts_dir"]).resolve()
exports_dir = (APP_ROOT / cfg["artifacts"]["exports_dir"]).resolve()
for p in (parsed_dir, charts_dir, exports_dir): p.mkdir(parents=True, exist_ok=True)

st.title("🏠 Property & Airbnb")
st.caption("EUR incomes/outgoings converted to GBP at statement rate. Shows monthly net and occupancy. Parser for PDFs comes next.")

REQUIRED_COLS = [
    "date","nights","currency","statement_rate",
    "income_eur","cleaning_eur","platform_fees_eur","taxes_eur","other_eur"
]

def generate_demo_airbnb() -> pd.DataFrame:
    # one year of daily rows with stochastic bookings
    import numpy as np
    rng = pd.date_range(pd.Timestamp.today().normalize() - pd.DateOffset(years=1) + pd.offsets.Day(1),
                        periods=365, freq="D")
    g = np.random.default_rng(9)
    rows = []
    for d in rng:
        booked = g.random() < 0.45  # ~45% occupancy
        nights = 1 if booked else 0
        adr_eur = g.normal(120, 25) if booked else 0
        income = max(0, adr_eur * nights)
        cleaning = 30 if booked and (g.random() < 0.6) else 0
        fees = income * 0.14 if booked else 0
        taxes = income * 0.03 if booked else 0
        other = 0
        # random but stable-ish statement rate (EUR→GBP inverse)
        rate = round(g.normal(0.85, 0.02), 4)  # EUR * (1/rate) = GBP  (we divide later)
        rows.append([d.date(), nights, "EUR", rate, round(income,2), cleaning, round(fees,2), round(taxes,2), other])
    df = pd.DataFrame(rows, columns=REQUIRED_COLS)
    return df

def load_airbnb_df() -> tuple[pd.DataFrame, str]:
    # Look for CSV created earlier; otherwise generate demo
    patterns = ["*airbnb*.csv", "airbnb.csv", "demo_airbnb.csv"]
    candidates = []
    for pat in patterns:
        candidates.extend(sorted(parsed_dir.glob(pat)))
    if candidates:
        try:
            df = pd.read_csv(candidates[0])
            df = coerce_airbnb(df)
            if df.empty: raise ValueError("Empty after coercion")
            return df, f"Loaded {candidates[0].name}"
        except Exception as e:
            st.warning(f"Could not load {candidates[0].name} ({e}). Falling back to demo data.")
    demo = generate_demo_airbnb()
    out = parsed_dir / "demo_airbnb.csv"
    demo.to_csv(out, index=False)
    return demo, "Generated demo Airbnb dataset (365 days)"

# Upload placeholder (parser to come)
with st.expander("Upload Airbnb PDF statements – parser coming soon", expanded=False):
    _files = st.file_uploader("Upload Airbnb PDFs", type=["pdf"], accept_multiple_files=True)
    if _files:
        st.info("PDF parsing will be enabled next. For now, the page uses CSV if found, else demo data.")

df, status = load_airbnb_df()
st.success(status)

# Monthly summary chart
st.divider()
st.subheader("Monthly income vs outgoings vs net (GBP)")
monthly = monthly_summary(df)
fig = go.Figure()
fig.add_bar(name="Income (GBP)", x=monthly["month"], y=monthly["income_gbp"])
fig.add_bar(name="Fees (GBP)",   x=monthly["month"], y=monthly["fees_gbp"])
fig.add_bar(name="Taxes (GBP)",  x=monthly["month"], y=monthly["taxes_gbp"])
fig.add_bar(name="Cleaning (GBP)", x=monthly["month"], y=monthly["cleaning_gbp"])
fig.add_bar(name="Other (GBP)",  x=monthly["month"], y=monthly["other_gbp"])
fig.add_bar(name="Net (GBP)",    x=monthly["month"], y=monthly["net_gbp"])
fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)
with colA:
    if st.button("Export monthly chart (PNG/PDF)"):
        base = charts_dir / "airbnb_monthly_income_net"
        try:
            save_plotly_figure(fig, base)
            st.success(f"Saved {base.with_suffix('.png').name} / {base.with_suffix('.pdf').name}")
        except Exception as e:
            st.info(f"Image export needs 'kaleido'. Try: pip install kaleido. ({e})")

# Occupancy heatmap
st.divider()
st.subheader("Occupancy heatmap (1=occupied)")
heat = occupancy_heatmap(df)
fig_h = px.imshow(
    heat.values,
    labels=dict(x="Day of month", y="Month", color="Occupied"),
    x=list(heat.columns),
    y=list(heat.index),
    aspect="auto",
)
st.plotly_chart(fig_h, use_container_width=True)

with colB:
    if st.button("Export occupancy heatmap (PNG/PDF)"):
        base = charts_dir / "airbnb_occupancy_heatmap"
        try:
            save_plotly_figure(fig_h, base)
            st.success(f"Saved {base.with_suffix('.png').name} / {base.with_suffix('.pdf').name}")
        except Exception as e:
            st.info(f"Image export needs 'kaleido'. Try: pip install kaleido. ({e})")

# Data exports
st.divider()
st.subheader("Data exports")
st.download_button("Download monthly CSV", data=monthly.to_csv(index=False), file_name="airbnb_monthly_summary.csv")

with st.expander("Download XLSX (monthly + raw)"):
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xw:
            monthly.to_excel(xw, index=False, sheet_name="Monthly")
            coerce_airbnb(df).to_excel(xw, index=False, sheet_name="Raw")
        st.download_button("Download XLSX", data=buf.getvalue(), file_name="airbnb_summary.xlsx")
    except Exception as e:
        st.info(f"Could not create XLSX. Use CSV instead. ({e})")
