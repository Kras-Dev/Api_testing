#src/api/models.py
from datetime import date

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ParamBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

class BookingDates(ParamBaseModel):
    check_in: date = Field(..., alias="checkin", description="Дата заезда")
    check_out: date = Field(..., alias="checkout", description="Дата выезда")

    @field_validator("check_out", mode="after")
    @classmethod
    def validate_dates(cls, value: date, info) -> date:
        check_in = info.data.get("check_in") if info.data else None
        if check_in and value <= check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return value

class Booking(ParamBaseModel):
    first_name: str = Field(..., min_length=1, alias="firstname")
    last_name: str = Field(..., min_length=1, alias="lastname")
    total_price: float = Field(..., ge=0, alias="totalprice")
    deposit_paid: bool = Field(default=False, alias="depositpaid")
    booking_dates: BookingDates = Field(..., alias="bookingdates")
    additional_needs: str | None = Field(default=None, alias="additionalneeds")

class BookingResponse(Booking):
    booking_id: int = Field(alias="bookingid")

class AuthRequest(ParamBaseModel):
    user_name: str = Field(alias="username")
    password: str

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

class AuthResponse(ParamBaseModel):
    token: str

class ErrorResponse(ParamBaseModel):
    message: str

