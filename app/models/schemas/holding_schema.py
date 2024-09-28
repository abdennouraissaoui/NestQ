from typing import Optional
from pydantic import BaseModel, Field


class HoldingBaseSchema(BaseModel):
    symbol: Optional[str] = Field(description="Symbol or ticker of the investment")
    description: str = Field(description="Description or name of the investment")
    cusip: Optional[str] = Field(description="CUSIP of the investment")
    quantity: Optional[float] = Field(description="Quantity of the investment.")
    currency: str = Field(description="Currency of the holding")


class HoldingCreateSchema(HoldingBaseSchema):
    book_value: Optional[float] = Field(
        description="Book value or cost basis of the investment"
    )
    cost_per_share: Optional[float] = Field(
        description="Cost per share of the investment"
    )
    market_value: float = Field(description="Market value of the investment")
    current_price: Optional[float] = Field(
        description="Current price of the investment"
    )


class HoldingDisplaySchema(HoldingBaseSchema):
    id: int = Field(description="Unique identifier for the holding")
    market_value: float = Field(description="Market value of the investment")

    class Config:
        from_attributes = True


class HoldingUpdateSchema(BaseModel):
    quantity: Optional[float] = Field(description="Quantity of the investment.")
    market_value: Optional[float] = Field(description="Market value of the investment")
    current_price: Optional[float] = Field(
        description="Current price of the investment"
    )
