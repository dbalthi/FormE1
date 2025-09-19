import streamlit as st
from pathlib import Path
import time
from app._bootstrap import load_cfg

st.set_page_config(page_title="Upload & Parse", page_icon="📤", layout="wide")

cfg, APP_ROOT = load_cfg()
raw_dir    = APP_ROOT / cfg["data"]["raw_dir"]
parsed_dir = APP_ROOT / cfg["data"]["parsed_dir"]
raw_dir.mkdir(parents=True, exist_ok=True)
parsed_dir.mkdir(parents=True, exist_ok=True)

st.title("📤 Upload & Parse")
st.caption("Drop PDFs or screenshots. Parsing pipeline will expand (PDF tables → OCR fallback).")

uploaded = st.file_uploader("Upload files (PDF/PNG/JPG)", type=["pdf","png","jpg","jpeg"], accept_multiple_files=True)
if uploaded:
    for f in uploaded:
        (raw_dir / f.name).write_bytes(f.read())
    st.success(f"Saved {len(uploaded)} file(s) to {raw_dir}")

st.divider()
st.subheader("Parse (demo pipeline)")
if st.button("Run demo parse on uploads"):
    from datetime import datetime, timedelta
    import pandas as pd, numpy as np
    today = datetime.today().date()
    dates = pd.date_range(today - timedelta(days=365), today, freq="W")
    cats = ["Housing","Utilities","Groceries","Transport","Insurance","Medical","ChildrenMedical","School","Education","Leisure","Misc"]
    rng = np.random.default_rng(42)
    rows = []
    for d in dates:
        for _ in range(rng.integers(3, 8)):
            amt = float(rng.normal(50, 30))
            if amt <= 0: amt = abs(amt) + 10
            rows.append([d.date(), f"Vendor {rng.integers(1,200)}", f"Ref {rng.integers(1000,9999)}", -round(amt,2), "GBP", "ACCT-001", str(rng.choice(cats))])
    pd.DataFrame(rows, columns=["date","vendor","description","amount","currency","account","category"]).to_csv(parsed_dir / "demo_parsed_spending.csv", index=False)
    with st.spinner("Parsing..."): time.sleep(1.0)
    st.success("Demo parsed file generated.")
