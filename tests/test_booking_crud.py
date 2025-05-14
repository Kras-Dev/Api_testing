#tests/test_booking_crud.py

import allure
import pytest
from pydantic import ValidationError

from src.api.models import Booking
from src.api.routes import Routes

@pytest.mark.parametrize("booking_test_data", [
    {
        "firstname": "Alice",
        "lastname": "Smith",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-06-01",
            "checkout": "2025-06-10"
        },
        "additionalneeds": "Breakfast"
    },
    {
        "firstname": "Bob",
        "lastname": "Brown",
        "totalprice": 0,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2025-07-15",
            "checkout": "2025-07-20"
        },
        "additionalneeds": None
    },
])
@allure.feature("Booking CRUD Operations Tests")
class TestBookingCRUD:
    @allure.title("Создание бронирования с валидными данными")
    def test_create_booking(self, create_booking, booking_test_data):
        """
        Проверяет успешное создание бронирования с валидными данными.

        Проверяет, что возвращаемый ID бронирования положительный.
        """
        with allure.step("Создание бронирования"):
            booking_id, test_data = create_booking(booking_test_data)
        assert booking_id > 0, "ID бронирования должен быть положительным"

    @allure.title("Получение бронирования по ID")
    def test_get_booking(self, client, create_booking,booking_test_data):
        """
        Проверяет получение бронирования по ID.

        Сравнивает полученные данные с исходными.
        """
        with allure.step("Создание бронирования для получения"):
            booking_id, test_data = create_booking(booking_test_data)
        route = Routes.booking_by_id(booking_id)
        with allure.step(f"Получение бронирования с ID {booking_id}"):
            response = client.get_booking(route)
        assert response == Booking.model_validate(test_data)

    @allure.title("Обновление бронирования")
    @pytest.mark.parametrize("updated_test_data", [
        {
            "firstname": "UpdatedName",
            "totalprice": 200,
            "additionalneeds": "Lunch"
        }
    ])
    def test_update_booking(self, client, get_auth_token, create_booking,booking_test_data, updated_test_data):
        """
        Проверяет обновление бронирования с новыми данными.

        Проверяет, что обновлённые данные совпадают с ожидаемыми.
        """
        with allure.step("Создание бронирования для обновления"):
            booking_id, data = create_booking(booking_test_data)
        test_data = {**booking_test_data, **updated_test_data}
        updated_booking_test_data = Booking.model_validate(test_data)
        route = Routes.booking_by_id(booking_id)
        with allure.step(f"Обновление бронирования с ID {booking_id}"):
            response = client.update_booking(updated_booking_test_data, route, get_auth_token)
        assert response == Booking.model_validate(test_data)

    @allure.title("Удаление бронирования")
    def test_delete_booking(self, client, get_auth_token, create_booking, booking_test_data):
        """
        Проверяет удаление бронирования и невозможность его последующего получения.

        Ожидает ошибку 404 при попытке получить удалённое бронирование.
        """
        with allure.step("Создание бронирования для удаления"):
            booking_id, _ = create_booking(booking_test_data)
        route = Routes.booking_by_id(booking_id)
        with allure.step(f"Удаление бронирования с ID {booking_id}"):
            client.delete_booking(route, get_auth_token)
        with allure.step(f"Проверка отсутствия бронирования с ID {booking_id}"):
            with pytest.raises(RuntimeError) as exc_info:
                client.get_booking(route)
            assert "404" in str(exc_info.value)


@allure.feature("Booking Negative Tests")
class TestBookingNegative:
    @allure.title("Создание бронирования с некорректными датами (check_out <= check_in)")
    @pytest.mark.parametrize("invalid_test_data",[
        {
            "firstname": "Invalid",
            "lastname": "Dates",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-06-10",
                "checkout": "2025-06-01"  # Выезд раньше заезда
            },
            "additionalneeds": None
        },
    ])
    def test_create_booking_invalid_dates(self, client, invalid_test_data):
        """
        Проверяет, что создание бронирования с некорректными датами вызывает ошибку валидации.
        """
        with allure.step("Попытка создания бронирования с некорректными датами"):
            with pytest.raises(ValidationError) as exc_info:
                Booking.model_validate(invalid_test_data)
            assert "Дата выезда должна быть позже даты заезда" in str(exc_info.value)

    @allure.title("Создание бронирования с отрицательной ценой")
    @pytest.mark.parametrize("invalid_test_data",[
        {
            "firstname": "Invalid",
            "lastname": "Price",
            "totalprice": -50,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2025-06-01",
                "checkout": "2025-06-10"
            },
            "additionalneeds": None
        }
    ])
    def test_create_booking_negative_price(self, client, invalid_test_data):
        """
        Проверяет, что создание бронирования с отрицательной ценой вызывает ошибку валидации.
        """
        with allure.step("Пытаемся создать бронирование с отрицательной ценой"):
            with pytest.raises(ValidationError) as exc_info:
                Booking.model_validate(invalid_test_data)
            assert "Input should be greater than or equal to 0" in str(exc_info)

    @allure.title("Обновление бронирования без токена")
    @pytest.mark.parametrize("booking_test_data",[
        {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2025-06-01",
                "checkout": "2025-06-05"
            },
            "additionalneeds": None
        }
    ])
    def test_update_without_token(self, client, create_booking, booking_test_data):
        """
        Проверяет, что обновление бронирования без токена аутентификации вызывает ошибку авторизации.
        """
        with allure.step("Создание бронирования для обновления без токена"):
            booking_id, test_data = create_booking(booking_test_data)
        updated_test_data = {**test_data, "firstname": "NoToken"}
        updated_booking = Booking.model_validate(updated_test_data)
        route = Routes.booking_by_id(booking_id)
        with allure.step("Попытка обновления бронирования без токена"):
            with pytest.raises(RuntimeError) as exc_info:
                client.update_booking(updated_booking, route, token="")
            assert "401" in str(exc_info.value) or "403" in str(exc_info.value)

    @allure.title("Получение несуществующего бронирования")
    @pytest.mark.parametrize("non_existent_id", [99999999])
    def test_get_nonexistent_booking(self, client, non_existent_id):
        """
        Проверяет, что получение несуществующего бронирования вызывает ошибку 404
        """
        route = Routes.booking_by_id(non_existent_id)
        with allure.step(f"Попытка получения несуществующего бронирования с ID {non_existent_id}"):
            with pytest.raises(RuntimeError) as exc_info:
                client.get_booking(route)
            assert "404" in str(exc_info.value)

    @allure.title("Удаление несуществующего бронирования")
    @pytest.mark.parametrize("non_existent_id", [99999999])
    def test_delete_nonexistent_booking(self, client, get_auth_token, non_existent_id):
        """
        Проверяет, что удаление несуществующего бронирования вызывает ошибку 404 или 405.
        """
        route = Routes.booking_by_id(non_existent_id)
        with allure.step(f"Попытка удаления несуществующего бронирования с ID {non_existent_id}"):
            with pytest.raises(RuntimeError) as exc_info:
                client.delete_booking(route, get_auth_token)
            assert "404" or "405" in str(exc_info.value)
