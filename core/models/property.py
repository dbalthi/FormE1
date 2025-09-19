from pydantic import BaseModel
from datetime import date
from typing import Optional

class PropertyLine(BaseModel):
    date: date
    description: str
    amount_eur: float
    currency: str = "EUR"
    statement_rate: Optional[float] = None  # EUR->GBP

class PropertyPeriodSummary(BaseModel):
    month: str
    income_gbp: float
    fees_gbp: float
    taxes_gbp: float
    cleaning_gbp: float
    net_gbp: float
    occupancy_rate: float
