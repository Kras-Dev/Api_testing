#src/api/models.py
from datetime import date
from typing import  Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ParamBaseModel(BaseModel):
    """
    Базовая модель с настройками для всех моделей API.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        #alias_generator=pydantic.alias_generators.to_camel(),
    )

class BookingItem(ParamBaseModel):
    booking_id: int = Field(alias="bookingid", description="Уникальный идентификатор бронирования")

class BookingDates(ParamBaseModel):
    """
    Модель, описывающая даты бронирования.
    """
    check_in: date = Field(..., alias="checkin", description="Дата заезда")
    check_out: date = Field(..., alias="checkout", description="Дата выезда")

    @field_validator("check_out", mode="after")
    @classmethod
    def validate_dates(cls, value: date, info) -> date:
        """
        Валидатор, проверяющий, что дата выезда позже даты заезда.

        Args:
           value (date): Дата выезда.
           info: Информация о других полях модели.

        Returns:
           date: Валидированная дата выезда.

        Raises:
           ValueError: Если дата выезда не позже даты заезда.
        """
        check_in = info.data.get("check_in") if info.data else None
        if check_in and value <= check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return value

class Booking(ParamBaseModel):
    first_name: str = Field(..., min_length=1, alias="firstname", description="Имя клиента")
    last_name: str = Field(..., min_length=1, alias="lastname", description="Фамилия клиента")
    total_price: float = Field(..., ge=0, alias="totalprice", description="Общая стоимость бронирования")
    deposit_paid: bool = Field(default=False, alias="depositpaid", description="Оплачен ли депозит")
    booking_dates: BookingDates = Field(..., alias="bookingdates", description="Даты бронирования")
    additional_needs: Optional[str] = Field(default=None, alias="additionalneeds",
                                            description="Дополнительные пожелания клиента")

class BookingResponse(ParamBaseModel):
    booking_id: int = Field(alias="bookingid", description="Уникальный идентификатор созданного бронирования")
    booking: Booking = Field(..., description="Данные созданного бронирования")

class AuthRequest(ParamBaseModel):
    user_name: str = Field(alias="username", description="Имя пользователя для аутентификации")
    password: str = Field(..., description="Пароль пользователя")


class AuthResponse(ParamBaseModel):
    token: str = Field(..., description="Токен аутентификации пользователя")

class ErrorResponse(ParamBaseModel):
        message: str = Field(..., description="Сообщение об ошибке API")
