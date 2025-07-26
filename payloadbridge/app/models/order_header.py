from typing import Optional
from pydantic import BaseModel, Field, constr
from datetime import date
from enum import Enum

class EvergreenFlag(str, Enum):
    Y = 'Y'
    N = 'N'

class OrderHeader(BaseModel):
    orderNumber: Optional[str]
    orderType: str = Field(..., min_length=1, strip_whitespace=True)
    orderCategory: str = Field(..., min_length=1, strip_whitespace=True)
    businessUnit: str = Field(..., min_length=1, strip_whitespace=True)
    hdrEffectiveStartDate: date
    hdrEffectiveEndDate: Optional[date]
    hdrBillToCustAccountNum: str = Field(..., min_length=1, strip_whitespace=True)
    hdrEvergreenFlag: Optional[EvergreenFlag]
    # ... add other header fields as needed ...
