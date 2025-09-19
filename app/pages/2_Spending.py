import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from app._bootstrap import load_cfg
from core.export.charts import save_plotly_figure

# Optional: simple keyword rules if available
try:
    from core.classify.rules import load_categories, classify_vendor
except Exception:
    load_categories = classify_vendor = None

st.set_page_config(page_title="Spending Analysis", page_icon="📊", layout="wide")

cfg, APP_ROOT = load_cfg()
parsed_dir = APP_ROOT / cfg["data"]["parsed_dir"]
charts_dir = APP_ROOT / cfg["artifacts"]["charts_dir"]
exports_dir = APP_ROOT / cfg["artifacts"]["exports_dir"]
charts_dir.mkdir(parents=True, exist_ok=True)
exports_dir.mkdir(parents=True, exist_ok=True)

st.title("📊 Spending Analysis")
st.caption("Interactive, court-ready visuals with drill-downs and chart exports.")

# ---------------- helpers ----------------
DATE_CANDIDATES = ["date","Date","Transaction Date","Posted Date"]
AMOUNT_CANDIDATES = ["amount","Amount","Transaction Amount","Money In","Money Out","Debit","Credit"]
DESC_CANDIDATES = ["vendor","Vendor","merchant","Merchant","description","Description","Details","Narrative","Memo"]

def pick_col(df: pd.DataFrame, names: list[str]) -> str | None:
    for n in names:
        if n in df.columns: return n
    return None

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- date ---
    c_date = pick_col(df, DATE_CANDIDATES)
    if not c_date:
        raise ValueError("No date column found.")
    df["date"] = pd.to_datetime(df[c_date], errors="coerce")
    df = df.dropna(subset=["date"])

    # --- amount ---
    if "amount" in df.columns:
        amt = df["amount"]
    else:
        # build from common schemas
        debit = pick_col(df, ["debit","Debit","Money Out"])
        credit = pick_col(df, ["credit","Credit","Money In"])
        if debit and credit:
            amt = pd.to_numeric(df[credit], errors="coerce").fillna(0) - pd.to_numeric(df[debit], errors="coerce").fillna(0)
        else:
            c_amt = pick_col(df, AMOUNT_CANDIDATES)
            if not c_amt:
                raise ValueError("No amount column found.")
            amt = pd.to_numeric(df[c_amt], errors="coerce")
    df["amount"] = amt.fillna(0.0)

    # --- vendor / description ---
    c_desc = pick_col(df, DESC_CANDIDATES)
    df["vendor"] = df[c_desc].astype(str) if c_desc else "Unknown"
    df["description"] = df["vendor"]

    # --- category fallback ---
    if "category" not in df.columns:
        df["category"] = "Uncategorized"

        # Try rules if available
        try:
            if load_categories and classify_vendor:
                cats_path = APP_ROOT / "config" / "categories.yml"
                if cats_path.exists():
                    cats = load_categories(cats_path)
                    df["category"] = df["vendor"].astype(str).apply(lambda v: classify_vendor(v, cats, default="Uncategorized"))
        except Exception:
            pass

    # final tidy
    keep = ["date","vendor","description","amount","category"]
    return df[keep].sort_values("date").reset_index(drop=True)

# ------------- load a parsed CSV -------------
def looks_like_spending(df: pd.DataFrame) -> bool:
    """Heuristic: does this CSV look like a transactions file (not Airbnb/Income)?"""
    cols = set(df.columns)
    # Airbnb/raw property signatures -> exclude
    airbnb_markers = {"income_eur","platform_fees_eur","taxes_eur","cleaning_eur","statement_rate","nights"}
    if cols & airbnb_markers:
        return False
    # Income signatures -> exclude
    income_markers = {"gross","paye","ee_ni","er_ni","pension_ee","pension_er","holiday_pay","net"}
    if cols & income_markers:
        return False
    # Spending signatures -> include
    spending_markers = {"amount","Amount","Transaction Amount","Money In","Money Out","Debit","Credit"}
    if cols & spending_markers:
        return True
    # Also allow if we have a date + description-like column
    date_candidates = set(DATE_CANDIDATES)
    desc_candidates = set(DESC_CANDIDATES)
    if (cols & set(date_candidates)) and (cols & set(desc_candidates)):
        return True
    return False

files_all = sorted(parsed_dir.glob("*.csv"))
if not files_all:
    st.warning("No parsed CSV found. Go to **Upload & Parse** and run the demo parse (or add your own).")
    st.stop()

# Prefer files that look like spending
spending_candidates = [p for p in files_all if looks_like_spending(pd.read_csv(p, nrows=200))]
if not spending_candidates:
    st.warning(
        "I found CSVs, but none look like spending/transactions.\n\n"
        "Tip: Go to **Upload & Parse** and click **Run demo parse** to create a transactions CSV."
    )
    st.stop()

# Let the user confirm which CSV to use (default = first decent match)
choice = st.selectbox(
    "Choose a transactions CSV",
    options=[p.name for p in spending_candidates],
    index=0,
)
chosen_path = next(p for p in spending_candidates if p.name == choice)

raw = pd.read_csv(chosen_path)
try:
    df = normalize(raw)
except Exception as e:
    st.error(f"Could not normalize `{chosen_path.name}`: {e}")
    st.stop()
