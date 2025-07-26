# Consolidated and improved OrderLine and OrderPayload models for production use


from typing import List, Optional
from pydantic import BaseModel, Field, root_validator
from datetime import date
from enum import Enum
from app.utils.validators import validate_evergreen_and_end_date



class EvergreenFlag(str, Enum):
    Y = 'Y'
    N = 'N'


class OrderLine(BaseModel):
    lineNumber: str = Field(..., min_length=1, strip_whitespace=True)
    lineType: str = Field(..., min_length=1, strip_whitespace=True)
    lineEffectiveStartDate: date
    lineEffectiveEndDate: Optional[date]
    lineEvergreenFlag: Optional[EvergreenFlag]
    itemName: Optional[str]
    itemDescription: Optional[str]
    uom: Optional[str]
    quantity: Optional[float] = Field(None, ge=0)
    unitPrice: Optional[float] = Field(None, ge=0)
    lineStatus: Optional[str]
    trackingOptions: Optional[str]
    lineBillingCycle: Optional[str]
    lineBillingFrequency: Optional[str]
    lineInvoicingRule: Optional[str]
    lineBillingChannel: Optional[str]
    lineDeliveryChannel: Optional[str]
    # ... add all other fields as needed ...

    @root_validator
    def validate_evergreen_and_end_date(cls, values):
        validate_evergreen_and_end_date(values.get('lineEvergreenFlag'), values.get('lineEffectiveEndDate'))
        return values


class OrderPayload(BaseModel):
    orderNumber: Optional[str]
    orderType: str = Field(..., min_length=1, strip_whitespace=True)
    orderCategory: str = Field(..., min_length=1, strip_whitespace=True)
    businessUnit: str = Field(..., min_length=1, strip_whitespace=True)
    hdrEffectiveStartDate: date
    hdrEffectiveEndDate: Optional[date]
    hdrBillToCustAccountNum: str = Field(..., min_length=1, strip_whitespace=True)
    hdrEvergreenFlag: Optional[EvergreenFlag]
    orderLines: List[OrderLine]
    # ... add all other header fields as needed ...

    @root_validator
    def validate_header_fields(cls, values):
        if values.get('hdrEvergreenFlag') == EvergreenFlag.N and not values.get('hdrEffectiveEndDate'):
            raise ValueError('hdrEffectiveEndDate is required for non-evergreen orders')
        if not values.get('orderLines') or not isinstance(values['orderLines'], list) or len(values['orderLines']) == 0:
            raise ValueError('At least one order line is required')
        return values
