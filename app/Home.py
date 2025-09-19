import streamlit as st
import pandas as pd
from pathlib import Path
from app._bootstrap import load_cfg

st.set_page_config(page_title="FormE1 – Home", page_icon="📑", layout="wide")

cfg, APP_ROOT = load_cfg()
raw_dir    = APP_ROOT / cfg["data"]["raw_dir"]
parsed_dir = APP_ROOT / cfg["data"]["parsed_dir"]
raw_dir.mkdir(parents=True, exist_ok=True)
parsed_dir.mkdir(parents=True, exist_ok=True)

st.title("📑 FormE1 – Stéphanie Parthenay")
st.caption("Privacy-first preparation of UK Form E1 with advanced visuals and drill-downs.")

# quick diag (you can remove later)
st.write("APP_ROOT:", str(APP_ROOT))
st.write("Config path:", str(APP_ROOT / "config" / "app.toml"))

c1, c2, c3 = st.columns(3)
c1.metric("Raw files",   len(list(raw_dir.glob("*"))))
c2.metric("Parsed files",len(list(parsed_dir.glob("*.csv"))))
c3.metric("Time window", "Last 12 months")

st.divider()
st.subheader("Quick Links")
st.page_link("pages/1_Upload.py",   label="📤 Upload & Parse")
st.page_link("pages/2_Spending.py", label="📊 Spending Analysis")
st.page_link("pages/3_Income.py",   label="💼 Employment Income (Parasol)")
st.page_link("pages/4_Property.py", label="🏠 Property & Airbnb")
st.page_link("pages/5_FormE1.py",   label="🧾 Form E1 Outputs")
st.page_link("pages/6_Settings.py", label="⚙️ Settings")

st.divider()
st.subheader("Recent Parsed Preview")
csvs = sorted(parsed_dir.glob("*.csv"), reverse=True)
if csvs:
    df = pd.read_csv(csvs[0]).head(20)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No parsed files yet. Use **Upload & Parse** to add statements.")
