#tests/conftest.py

import logging
import allure
import pytest
from src.api.client import BookerClient
from src.api.models import Booking
from src.api.routes import Routes
from src.config import settings
import random

@pytest.fixture(scope="session")
def client() -> BookerClient():
    """
    Фикстура для создания и управления клиентом BookerClient.

    Создаёт экземпляр клиента для работы с API бронирования, используемый в тестах на протяжении всей сессии.
    После завершения тестовой сессии закрывает клиент, освобождая ресурсы.

    Returns:
        BookerClient: экземпляр клиента для взаимодействия с API.
    """
    client = BookerClient()
    yield client
    try:
        client.close()
    except Exception as e:
        logging.warning(f"Ошибка при закрытии клиента: {e}")

@pytest.fixture(scope="session")
def create_booking(client: BookerClient):
    """
    Фикстура для создания бронирования через API.

    Возвращает функцию, которая принимает данные бронирования, валидирует их и создаёт бронирование.
    Все созданные бронирования будут удалены после завершения сессии тестов.

    Returns:
        function: Функция для создания бронирования, возвращающая кортеж (booking_id, исходные данные).
    """
    created_ids: list[int] = []

    def _create(booking_data, route=Routes.BOOKING):
        booking = Booking.model_validate(booking_data)
        with allure.step("Создаем бронирование"):
            response = client.create_booking(booking, route)
            created_ids.append(response.booking_id)
            return response.booking_id, booking_data

    yield _create

    if created_ids:
        token = client.authenticate(settings.user_name, settings.password, Routes.AUTH).token
        for booking_id in created_ids:
            with allure.step(f"Удаление бронирования с ID {booking_id}"):
                try:
                    delete_route = Routes.booking_by_id(booking_id)
                    client.delete_booking(delete_route, token)
                except Exception as e:
                    logging.warning(f"Ошибка при удалении бронирования {booking_id}: {e}")
                    pass

@pytest.fixture(scope="session")
def get_auth_token(client: BookerClient) -> str:
    """
    Фикстура для получения токена аутентификации.

    Используется для авторизации запросов к API.

    Args:
       client (BookerClient): клиент для работы с API.

    Returns:
       str: токен аутентификации.
    """
    with allure.step("Получение токена аутентификации"):
        auth_response = client.authenticate(settings.user_name, settings.password, Routes.AUTH)
    return auth_response.token

@pytest.fixture(scope="session")
def default_booking_test_data():
    pass

@pytest.fixture(scope="session")
def created_booking_once(client, create_booking, default_booking_test_data):
    """
    Фикстура, которая создаёт бронирование один раз за сессию

    Returns:
        booking_id и данные.
    """
    booking_id, data = create_booking(default_booking_test_data)

    yield booking_id, data

    token = client.authenticate(settings.user_name, settings.password, Routes.AUTH).token
    try:
        client.delete_booking(Routes.booking_by_id(booking_id), token)
    except Exception as e:
        logging.warning(f"Ошибка при удалении бронирования {booking_id}: {e}")

@pytest.fixture(scope="function")
def random_booking_id(client) -> int:
    booking_ids = client.get_booking_ids(Routes.BOOKING)
    if not booking_ids:
        pytest.skip("Нет доступных бронирований для выбора случайного ID")
    return random.choice(booking_ids).booking_id