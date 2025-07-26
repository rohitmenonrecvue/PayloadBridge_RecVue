from pydantic import BaseModel, Field
from typing import Optional, List

class OrderLine(BaseModel):
    product_id: str = Field(..., description="The ID of the product")
    quantity: int = Field(..., ge=1, description="The quantity of the product, must be greater than 0")
    price: float = Field(..., gt=0, description="The price of the product, must be greater than 0")

class Payload(BaseModel):
    order_id: str = Field(..., description="The unique identifier for the order")
    customer_id: str = Field(..., description="The unique identifier for the customer")
    order_lines: List[OrderLine] = Field(..., description="A list of order lines associated with the order")
    notes: Optional[str] = Field(None, description="Optional notes for the order")