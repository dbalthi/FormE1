from __future__ import annotations
import pandas as pd

REQUIRED_COLS = [
    "date", "nights", "currency", "statement_rate",
    "income_eur", "cleaning_eur", "platform_fees_eur", "taxes_eur", "other_eur"
]

def coerce_airbnb(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = 0.0 if c not in ("date","currency") else ("EUR" if c=="currency" else pd.NaT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    # numeric
    num = [c for c in REQUIRED_COLS if c not in ("date","currency")]
    df[num] = df[num].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    # derived GBP
    rate = df["statement_rate"].replace(0, pd.NA).fillna(1.0)  # fallback
    df["income_gbp"]   = (df["income_eur"]   / rate).round(2)
    df["cleaning_gbp"] = (df["cleaning_eur"] / rate).round(2)
    df["fees_gbp"]     = (df["platform_fees_eur"] / rate).round(2)
    df["taxes_gbp"]    = (df["taxes_eur"] / rate).round(2)
    df["other_gbp"]    = (df["other_eur"]  / rate).round(2)
    df["outgoings_gbp"] = (df["cleaning_gbp"] + df["fees_gbp"] + df["taxes_gbp"] + df["other_gbp"]).round(2)
    df["net_gbp"] = (df["income_gbp"] - df["outgoings_gbp"]).round(2)
    return df.dropna(subset=["date"]).sort_values("date")

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = coerce_airbnb(df)
    s = pd.DataFrame(df)
    s["month"] = pd.to_datetime(s["date"]).dt.to_period("M").astype(str)
    grp = s.groupby("month", as_index=False).agg({
        "income_gbp":"sum","fees_gbp":"sum","taxes_gbp":"sum","cleaning_gbp":"sum","other_gbp":"sum","net_gbp":"sum","nights":"sum"
    })
    return grp

def occupancy_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a pivot with rows=Month, cols=Day (1..31), values=occupied (0/1*nights>0).
    If nights > 0 on a date → mark occupied.
    """
    df = coerce_airbnb(df)
    s = pd.DataFrame(df)
    s["dt"] = pd.to_datetime(s["date"])
    s["month"] = s["dt"].dt.to_period("M").astype(str)
    s["day"] = s["dt"].dt.day
    s["occupied"] = (s["nights"] > 0).astype(int)
    pivot = s.pivot_table(index="month", columns="day", values="occupied", aggfunc="max", fill_value=0)
    # ensure 1..31 columns exist
    for d in range(1, 32):
        if d not in pivot.columns:
            pivot[d] = 0
    pivot = pivot[sorted(pivot.columns)]
    return pivot.sort_index()
