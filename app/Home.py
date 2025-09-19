import streamlit as st
import pandas as pd
from pathlib import Path
import datetime

from app._bootstrap import load_cfg

# ----------------------------------
# Page config
# ----------------------------------
st.set_page_config(
    page_title="FormE1 – Home",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",   # keep sidebar open
)

# ----------------------------------
# Load config & paths
# ----------------------------------
cfg, APP_ROOT = load_cfg()
raw_dir    = APP_ROOT / cfg["data"]["raw_dir"]
parsed_dir = APP_ROOT / cfg["data"]["parsed_dir"]
raw_dir.mkdir(parents=True, exist_ok=True)
parsed_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------
# Sidebar branding
# ----------------------------------
logo_path = (APP_ROOT / "assets" / "logo.png").resolve()
with st.sidebar:
    st.markdown("### 🧾 FormE1 Helper")
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.caption("No logo found at /assets/logo.png")
    st.caption("Spending • Income • Property • Form E1")

# ----------------------------------
# Main content
# ----------------------------------
st.title("📑 FormE1 – Stéphanie Parthenay")
st.caption("Privacy-first preparation of UK Form E1 with advanced visuals and drill-downs.")

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Raw files",   len(list(raw_dir.glob('*'))))
c2.metric("Parsed files",len(list(parsed_dir.glob('*.csv'))))
c3.metric("Time window", "Last 12 months")

# Quick links
st.divider()
st.subheader("Quick Links")
st.page_link("pages/1_Upload.py",   label="📤 Upload & Parse")
st.page_link("pages/2_Spending.py", label="📊 Spending Analysis")
st.page_link("pages/3_Income.py",   label="💼 Employment Income (Parasol)")
st.page_link("pages/4_Property.py", label="🏠 Property & Airbnb")
st.page_link("pages/5_FormE1.py",   label="🧾 Form E1 Outputs")
st.page_link("pages/6_Settings.py", label="⚙️ Settings")

# Recent parsed preview
st.divider()
st.subheader("Recent Parsed Preview")
parsed_csvs = sorted(parsed_dir.glob("*.csv"), reverse=True)
if parsed_csvs:
    df = pd.read_csv(parsed_csvs[0]).head(20)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No parsed files yet. Use **Upload & Parse** to add statements.")

# Footer timestamp
st.divider()
st.caption(f"🕒 Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
