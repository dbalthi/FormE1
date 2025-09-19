import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app._bootstrap import load_cfg
from core.income.calculators import weekly_to_monthly, rolling_12m_totals, build_waterfall_row
from core.export.charts import save_plotly_figure

st.set_page_config(page_title="Employment Income (Parasol)", page_icon="💼", layout="wide")

# ---- paths & dirs
cfg, APP_ROOT = load_cfg()
parsed_dir  = (APP_ROOT / cfg["data"]["parsed_dir"]).resolve()
charts_dir  = (APP_ROOT / cfg["artifacts"]["charts_dir"]).resolve()
exports_dir = (APP_ROOT / cfg["artifacts"]["exports_dir"]).resolve()
for p in (parsed_dir, charts_dir, exports_dir): p.mkdir(parents=True, exist_ok=True)

st.title("💼 Employment Income (Parasol)")
st.caption("Demo-safe page: generates synthetic weekly payslips if none found. Parser for real PDFs will be added next.")

# ---------------------------
# Helpers
# ---------------------------
REQUIRED_COLS = [
    "period_end","gross","paye","ee_ni","er_ni","pension_ee","pension_er",
    "holiday_pay","other_deductions","student_loan","net"
]

def generate_demo_payslips() -> pd.DataFrame:
    import numpy as np
    rng = pd.date_range(pd.Timestamp.today().normalize() - pd.DateOffset(years=1), periods=52, freq="W-FRI")
    rows = []
    g = np.random.default_rng(17)
    for d in rng:
        gross = float(max(900, g.normal(1200, 80)))
        paye  = round(gross * 0.18, 2)
        ee_ni = round(gross * 0.09, 2)
        er_ni = round(gross * 0.11, 2)
        pens_ee = round(gross * 0.03, 2)
        pens_er = round(gross * 0.03, 2)
        holiday = 0.00  # set >0 if rolled-up
        other = float(max(0, g.normal(8, 6)))
        student = 0.0
        net = round(gross - (paye + ee_ni + pens_ee + other + student) + holiday, 2)
        rows.append([d.date(), gross, paye, ee_ni, er_ni, pens_ee, pens_er, holiday, other, student, net])
    df = pd.DataFrame(rows, columns=REQUIRED_COLS)
    return df

def coerce_income(df: pd.DataFrame) -> pd.DataFrame:
    """Make sure required columns exist and types are correct; never crash."""
    df = df.copy()
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = 0.0
    df["period_end"] = pd.to_datetime(df["period_end"], errors="coerce").dt.date
    for c in REQUIRED_COLS:
        if c != "period_end":
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["period_end"]).sort_values("period_end")
    return df

def load_income_df() -> tuple[pd.DataFrame, str]:
    """Load first matching CSV; if missing or invalid, auto-generate demo."""
    # Preferred naming for real exports later:
    patterns = ["*parasol*_income*.csv", "parasol_income.csv", "demo_parasol_income.csv"]
    candidates = []
    for pat in patterns:
        candidates.extend(sorted(parsed_dir.glob(pat)))
    if candidates:
        try:
            df = pd.read_csv(candidates[0])
            df = coerce_income(df)
            if df.empty:
                raise ValueError("CSV had no valid rows.")
            return df, f"Loaded {candidates[0].name}"
        except Exception as e:
            st.warning(f"Could not load {candidates[0].name} ({e}). Falling back to demo data.")
    # Fallback: demo
    demo = generate_demo_payslips()
    out = parsed_dir / "demo_parasol_income.csv"
    demo.to_csv(out, index=False)
    return demo, "Generated demo payslips (52 weeks)"

# ---------------------------
# UI – Upload area (placeholder)
# ---------------------------
with st.expander("Upload Parasol payslips (PDF) – parser coming soon", expanded=False):
    _files = st.file_uploader("Upload Parasol PDF payslips", type=["pdf"], accept_multiple_files=True)
    if _files:
        st.info("PDF parsing will be enabled next. For now, demo data is used automatically if no CSV is present.")

# ---------------------------
# Load (or create) data safely
# ---------------------------
df, status_msg = load_income_df()
st.success(status_msg)

# ---------------------------
# Weekly waterfall
# ---------------------------
st.divider()
st.subheader("Weekly breakdown")

if df.empty:
    st.info("No income rows available yet.")
    st.stop()

sel = st.selectbox("Select week (period end)", options=sorted(df["period_end"], reverse=True))
wk = df[df["period_end"] == sel].iloc[0]
steps = build_waterfall_row(wk)
fig = go.Figure(go.Waterfall(
    name="Income",
    orientation="v",
    measure=[s["measure"] for s in steps],
    x=[s["name"] for s in steps],
    y=[s["value"] for s in steps],
))
fig.update_layout(title=f"Weekly Waterfall – period end {sel}")
st.plotly_chart(fig, use_container_width=True)

colA, colB = st.columns(2)
with colA:
    if st.button("Export waterfall (PNG/PDF)"):
        base = charts_dir / f"parasol_waterfall_{sel}"
        try:
            save_plotly_figure(fig, base)
            st.success(f"Saved {base.with_suffix('.png').name} / {base.with_suffix('.pdf').name}")
        except Exception as e:
            st.info(f"Image export needs 'kaleido'. Try: pip install kaleido. ({e})")

# ---------------------------
# Monthly & 12-month rollups
# ---------------------------
st.divider()
st.subheader("Monthly and 12-month totals")

monthly = weekly_to_monthly(df)
st.dataframe(monthly, use_container_width=True)

tot = rolling_12m_totals(df)
tot_df = pd.DataFrame([tot])
st.write("**Rolling 12-month totals**")
st.dataframe(tot_df, use_container_width=True)

with colB:
    # CSV export (always safe)
    st.download_button(
        "Download monthly CSV",
        data=monthly.to_csv(index=False),
        file_name="parasol_monthly_totals.csv"
    )

# Combined XLSX export (best-effort)
with st.expander("Download XLSX (monthly + 12M)"):
    try:
        from pandas import ExcelWriter
        buf = io.BytesIO()
        with ExcelWriter(buf, engine="openpyxl") as xw:
            monthly.to_excel(xw, index=False, sheet_name="Monthly")
            tot_df.to_excel(xw, index=False, sheet_name="12M_Totals")
        st.download_button("Download XLSX", data=buf.getvalue(), file_name="parasol_income_summary.xlsx")
    except Exception as e:
        st.info(f"Could not create XLSX (using openpyxl). You can use CSV instead. ({e})")
