from typing import List, Optional, Any
from pydantic import BaseModel, Field, root_validator, validator
from datetime import date

class OrderLine(BaseModel):
    lineNumber: str
    itemName: Optional[str]
    itemDescription: Optional[str]
    uom: Optional[str]
    quantity: Optional[str]
    unitPrice: Optional[str]
    lineEffectiveStartDate: date
    lineEffectiveEndDate: Optional[date]
    lineStatus: Optional[str]
    lineType: str
    trackingOptions: Optional[str]
    lineBillingCycle: Optional[str]
    lineBillingFrequency: Optional[str]
    lineInvoicingRule: Optional[str]
    lineEvergreenFlag: Optional[str]
    lineBillingChannel: Optional[str]
    lineDeliveryChannel: Optional[str]
    # ... add all other fields as needed ...

    @root_validator
    def check_required_fields(cls, values):
        if not values.get("lineNumber"):
            raise ValueError("Line number cannot be blank")
        if not values.get("lineType"):
            raise ValueError("Line type is required")
        if not values.get("lineEffectiveStartDate"):
            raise ValueError("Line start date is required")
        # Add more conditional/complex rules here as needed
        return values

class OrderPayload(BaseModel):
    orderNumber: Optional[str]
    orderType: str
    orderCategory: str
    businessUnit: str
    hdrEffectiveStartDate: date
    hdrEffectiveEndDate: Optional[date]
    hdrBillToCustAccountNum: str
    hdrEvergreenFlag: Optional[str]
    orderLines: List[OrderLine]
    # ... add all other header fields as needed ...

    @root_validator
    def check_header_fields(cls, values):
        if not values.get("orderType"):
            raise ValueError("Order type is required")
        if not values.get("orderCategory"):
            raise ValueError("Order category cannot be blank")
        if not values.get("businessUnit"):
            raise ValueError("Business Unit cannot be blank")
        if not values.get("hdrEffectiveStartDate"):
            raise ValueError("Effective start date is required")
        if values.get("hdrEvergreenFlag") == "N" and not values.get("hdrEffectiveEndDate"):
            raise ValueError("End date required for non-evergreen orders")
        # Add more conditional/complex rules here as needed
        return values
