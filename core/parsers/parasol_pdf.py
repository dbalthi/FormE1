from __future__ import annotations
from pathlib import Path
import pandas as pd

def parse_parasol_pdf(pdf_path: Path) -> pd.DataFrame:
    """
    Placeholder for Parasol payslip parsing.
    Expected output columns:
      period_end, gross, paye, ee_ni, er_ni, pension_ee, pension_er,
      holiday_pay, other_deductions, student_loan, net
    """
    raise NotImplementedError("Parasol PDF parsing will be implemented next.")
