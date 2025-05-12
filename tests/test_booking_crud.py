#tests/test_booking_crud.py

import allure
import pytest
from src.api.models import Booking
from src.api.routes import Routes


@allure.feature("Booking CRUD Operations")
class TestBookingCRUD:
    @pytest.mark.parametrize("booking_data",[
        {
            "firstname": "Alice",
            "lastname": "Smith",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2024-06-01",
                "checkout": "2024-06-10"
            },
            "additionalneeds": "Breakfast"
        },
        # {
        #     "firstname": "Bob",
        #     "lastname": "Brown",
        #     "totalprice": 0,
        #     "depositpaid": False,
        #     "bookingdates": {
        #         "checkin": "2024-07-15",
        #         "checkout": "2024-07-20"
        #     },
        #     "additionalneeds": None
        # },
    ])
    @allure.title("Создание бронирования с валидными данными")
    def test_create_booking(self, client, booking_data):
        booking = Booking.model_validate(booking_data, by_alias=True)
        booking_response = client.create_booking(booking, Routes.BOOKING)
        assert booking_response.first_name == booking.first_name
        assert booking_response.booking_dates.check_in == booking.booking_dates.check_in

    # @pytest.mark.parametrize("booking_data", booking_test_data)
    # @allure.title("Получение бронирования по ID")
    # def test_get_booking(self, client, booking_data):
    #     booking = Booking.model_validate(booking_data)
    #     booking_response = client.create_booking(booking)
    #     fetched_booking = client.get_booking(booking_response.bookingid)
    #     assert fetched_booking.firstname == booking.firstname
    #     assert fetched_booking.bookingdates.checkout == booking.bookingdates.checkout
    #
    # @pytest.mark.parametrize("booking_data", booking_test_data)
    # @allure.title("Обновление бронирования")
    # def test_update_booking(self, client, auth_token, booking_data):
    #     booking = Booking.model_validate(booking_data)
    #     booking_response = client.create_booking(booking)
    #     updated_booking = booking.copy(update={"firstname": "UpdatedName"})
    #     updated = client.update_booking(booking_response.bookingid, updated_booking, auth_token)
    #     assert updated.firstname == "UpdatedName"
    #
    # @pytest.mark.parametrize("booking_data", booking_test_data)
    # @allure.title("Удаление бронирования")
    # def test_delete_booking(self, client, auth_token, booking_data):
    #     booking = Booking.model_validate(booking_data)
    #     booking_response = client.create_booking(booking)
    #     client.delete_booking(booking_response.bookingid, auth_token)
    #     with pytest.raises(RuntimeError) as e:
    #         client.get_booking(booking_response.bookingid)
    #     assert "404" in str(e.value)





