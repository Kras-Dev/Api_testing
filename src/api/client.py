#src/api/client.py
import logging

import httpx
from pydantic import ValidationError
from typing import List, Optional
from src.api.models import Booking, BookingResponse, ErrorResponse, AuthResponse, AuthRequest, BookingItem
from src.config import settings

class BookerClient:
    def __init__(self, base_url: str = settings.base_url):
        """
        Инициализирует BookerClient.

        Args:
           base_url (str): Базовый URL API. По умолчанию берётся из настроек.
        """
        self.client = httpx.Client(base_url=base_url, timeout=10.0)
        self.base_url = base_url

    def get_booking_ids(self, route: str) -> List[BookingItem]:
        """
        Получает список ID бронирований.

        Args:
            route (str): Относительный путь API для получения списка бронирований.

        Returns:
            List[BookingItem]: Список объектов BookingItem с ID бронирований.
        """
        response = self.client.get(route)
        return [BookingItem.model_validate(item, by_alias=True) for item in response.json()]

    def create_booking(self, booking: Booking, route: str) -> BookingResponse:
        """
        Создаёт новое бронирование.

        Args:
          booking (Booking): Объект бронирования для создания.
          route (str): Относительный путь API для создания бронирования.
        Returns:
          BookingResponse: Ответ с информацией о созданном бронировании.
        Raises:
          RuntimeError: В случае ошибки API.
          ValueError: При ошибке валидации ответа.
        """
        headers = {"Content-Type": "application/json"}
        response = self.client.post(
            route,
            content=booking.model_dump_json(by_alias=True),
            headers=headers,
        )
        return self._handle_response(response, BookingResponse)

    def get_booking(self, route: str) -> Booking:
        """
        Получает данные бронирования.

        Args:
            route (str): Относительный путь API для получения бронирования.

        Returns:
            Booking: Объект бронирования.

        Raises:
            RuntimeError: В случае ошибки API.
            ValueError: При ошибке валидации ответа.
        """
        response = self.client.get(route)
        return self._handle_response(response, Booking)

    def update_booking(self, booking: Booking, route: str, token: str) -> Booking:
        """
        Обновляет существующее бронирование.

        Args:
            booking (Booking): Объект бронирования с обновлёнными данными.
            route (str): Относительный путь API для обновления бронирования.
            token (str): Токен аутентификации пользователя.

        Returns:
            Booking: Обновлённый объект бронирования.

        Raises:
            RuntimeError: В случае ошибки API.
            ValueError: При ошибке валидации ответа.
        """
        headers = {"Content-Type": "application/json", "Cookie": f"token={token}"}
        response = self.client.put(
            route,
            content=booking.model_dump_json(by_alias=True),
            headers=headers
        )
        return self._handle_response(response, Booking)

    def delete_booking(self, route: str, token: str) -> Optional[int]:
        """
        Удаляет бронирование.

        Args:
           route (str): Относительный путь API для удаления бронирования.
           token (str): Токен аутентификации пользователя.

        Returns:
           Optional[int]: Код статуса 201 при успешном удалении, иначе None.

        Raises:
           RuntimeError: В случае ошибки API.
        """
        headers = {"Cookie": f"token={token}"}
        response = self.client.delete(route, headers=headers)
        if response.status_code == 201:
            return response.status_code
        else:
            self._handle_error(response)

    def authenticate(self, user_name:str, password: str, route: str) -> AuthResponse:
        """
        Аутентифицирует пользователя и получает токен.

        Args:
            user_name (str): Имя пользователя.
            password (str): Пароль пользователя.
            route (str): Относительный путь API для аутентификации.

        Returns:
            AuthResponse: Объект с токеном аутентификации.

        Raises:
            RuntimeError: В случае ошибки API.
            ValueError: При ошибке валидации ответа.
        """
        auth_request = AuthRequest(username=user_name, password=password)
        response = self.client.post(route, json=auth_request.model_dump(by_alias=True))
        return self._handle_response(response, AuthResponse)

    def _handle_response(self, response: httpx.Response, model):
        """
        Обрабатывает ответ API, валидирует и преобразует в модель Pydantic.

        Args:
            response (httpx.Response): HTTP ответ от API.
            model (BaseModel): Pydantic модель для валидации и парсинга.

        Returns:
            BaseModel: Валидированный объект pydantic модели.

        Raises:
            RuntimeError: Если ответ содержит ошибку.
            ValueError: Если валидация ответа не удалась.
        """
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                raise RuntimeError(f"Ошибка парсинга JSON: {e}, ответ: {response.text}")
            if isinstance(data, dict) and "reason" in data:
                raise RuntimeError(f"API Ошибка: {data['reason']}")
            try:
                return model.model_validate(response.json(), by_alias=True)
            except ValidationError as e:
                raise ValueError(f"Ошибка валидации ответа: {e}")
        else:
            self._handle_error(response)

    def _handle_error(self, response: httpx.Response) -> None:
        """
        Обрабатывает ошибочный ответ API и выбрасывает исключение.

        Args:
            response (httpx.Response): HTTP ответ с ошибкой.

        Raises:
            RuntimeError: Исключение с описанием ошибки.
        """
        try:
            error = ErrorResponse.model_validate(response.json())
            reason = error.message
        except (ValueError, ValidationError) as e:
            logging.warning(f"Ошибка парсинга ответа API: {e}")
            reason = response.text
        raise RuntimeError(f"HTTP Ошибка {response.status_code}: {reason}")

    def close(self) -> None:
        """
        Закрывает HTTP клиент, освобождая ресурсы.
        """
        self.client.close()