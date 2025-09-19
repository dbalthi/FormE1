from pydantic import BaseModel
from datetime import date
from typing import Optional

class Transaction(BaseModel):
    date: date
    description: str
    vendor: str
    amount: float           # negative = outflow, positive = inflow
    currency: str = "GBP"
    account: Optional[str] = None
    category: Optional[str] = None
