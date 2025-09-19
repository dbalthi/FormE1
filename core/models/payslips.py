from pydantic import BaseModel
from datetime import date
from typing import List

class PayslipLine(BaseModel):
    code: str
    description: str
    amount: float

class PayslipSummary(BaseModel):
    period_start: date
    period_end: date
    gross: float
    net: float
    deductions: List[PayslipLine]
