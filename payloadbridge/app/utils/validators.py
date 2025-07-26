from typing import Optional
from datetime import date
from app.models.order_line import EvergreenFlag

def validate_evergreen_and_end_date(flag: Optional[EvergreenFlag], end_date: Optional[date]) -> None:
    if flag == EvergreenFlag.Y and end_date is not None:
        raise ValueError('lineEffectiveEndDate should not be set if lineEvergreenFlag is Y')
    if flag == EvergreenFlag.N and end_date is None:
        raise ValueError('lineEffectiveEndDate is required if lineEvergreenFlag is N')
