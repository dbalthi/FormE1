from __future__ import annotations
import pandas as pd

DEDUCTIONS_COLS = ["paye", "ee_ni", "pension_ee", "other_deductions", "student_loan", "holiday_pay_deduction"]

REQUIRED_COLS = [
    "period_end","gross","paye","ee_ni","er_ni","pension_ee","pension_er",
    "holiday_pay","other_deductions","student_loan","net"
]

def coerce_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure columns exist and types are numeric/date."""
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = 0.0
    df["period_end"] = pd.to_datetime(df["period_end"]).dt.date
    num_cols = [c for c in REQUIRED_COLS if c != "period_end"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df.sort_values("period_end")

def weekly_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = coerce_frame(df.copy())
    s = pd.DataFrame(df)
    s["month"] = pd.to_datetime(s["period_end"]).dt.to_period("M").astype(str)
    grp = s.groupby("month", as_index=False).agg({
        "gross":"sum","paye":"sum","ee_ni":"sum","er_ni":"sum",
        "pension_ee":"sum","pension_er":"sum","holiday_pay":"sum",
        "other_deductions":"sum","student_loan":"sum","net":"sum"
    })
    return grp

def rolling_12m_totals(df: pd.DataFrame) -> dict:
    df = coerce_frame(df)
    if df.empty:
        return {k:0.0 for k in ["gross","paye","ee_ni","er_ni","pension_ee","pension_er","holiday_pay","other_deductions","student_loan","net"]}
    last_date = pd.to_datetime(df["period_end"]).max()
    window_start = (last_date - pd.DateOffset(years=1)).date()
    mask = pd.to_datetime(df["period_end"]) > pd.Timestamp(window_start)
    d = df.loc[mask]
    sums = d[["gross","paye","ee_ni","er_ni","pension_ee","pension_er","holiday_pay","other_deductions","student_loan","net"]].sum().to_dict()
    return {k: float(round(v,2)) for k,v in sums.items()}

def build_waterfall_row(week: pd.Series) -> list[dict]:
    """Return list of steps for a Plotly Waterfall from one weekly row."""
    return [
        {"name":"Gross", "value": float(week["gross"]), "measure":"relative"},
        {"name":"PAYE", "value": -float(week["paye"]), "measure":"relative"},
        {"name":"EE NI", "value": -float(week["ee_ni"]), "measure":"relative"},
        {"name":"Pension (EE)", "value": -float(week["pension_ee"]), "measure":"relative"},
        {"name":"Other", "value": -float(week["other_deductions"]), "measure":"relative"},
        {"name":"Student Loan", "value": -float(week.get("student_loan",0.0)), "measure":"relative"},
        {"name":"Holiday Pay", "value": float(week.get("holiday_pay",0.0)), "measure":"relative"},
        {"name":"Net", "value": float(week["net"]), "measure":"total"},
    ]
