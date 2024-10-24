from typing import Optional
from pydantic import BaseModel, Field


class HoldingBaseSchema(BaseModel):
    symbol: Optional[str] = Field(
        description="Symbol or ticker of the investment", example="AAPL"
    )
    description: str = Field(
        description="Description or name of the investment", example="Apple Inc."
    )
    cusip: Optional[str] = Field(
        description="CUSIP of the investment", example="037833100"
    )
    quantity: Optional[float] = Field(
        description="Quantity of the investment.", example=10.0
    )
    currency: str = Field(description="Currency of the holding", example="USD")
    book_value: Optional[float] = Field(
        description="Book value or cost basis of the investment", example=1000.00
    )
    cost_per_share: Optional[float] = Field(
        description="Cost per share of the investment", example=100.00
    )
    market_value: float = Field(
        description="Market value of the investment", example=1200.00
    )
    current_price: Optional[float] = Field(
        description="Current price of the investment", example=120.00
    )
    investment_type: Optional[str] = Field(
        description="Type of investment, e.g., Cash and Equivalents, Equities and equity funds",
        example="Equities",
    )


class HoldingCreateSchema(HoldingBaseSchema):
    pass


class HoldingDisplaySchema(HoldingBaseSchema):
    id: int = Field(description="Unique identifier for the holding", example=1)
    symbol: Optional[str] = Field(
        description="Symbol or ticker of the investment", example="AAPL"
    )
    created_at: int = Field(
        ..., description="Timestamp when the holding was created"
    )
    updated_at: int = Field(
        ..., description="Timestamp when the holding was last updated"
    )

    class Config:
        from_attributes = True


class HoldingUpdateSchema(HoldingBaseSchema):
    pass


class HoldingDetailDisplaySchema(HoldingDisplaySchema):
    pass
