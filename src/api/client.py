#src/api/client.py

import httpx
from pydantic import ValidationError

from src.api.models import Booking, BookingResponse, ErrorResponse, AuthResponse, AuthRequest
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
        response = self.client.post(
            route,
            content=booking.model_dump_json(by_alias=True),
            headers={"Content-Type": "application/json"},
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
        headers = {"Cookie": f"token={token}"}
        response = self.client.put(route, json=booking.model_dump(by_alias=True), headers=headers)
        return self._handle_response(response, Booking)

    def delete_booking(self, route: str, token: str) -> None:
        """
        Удаляет бронирование.

        Args:
           route (str): Относительный путь API для удаления бронирования.
           token (str): Токен аутентификации пользователя.

        Raises:
           RuntimeError: В случае ошибки API.
        """
        headers = {"Cookie": f"token={token}"}
        response = self.client.delete(route, headers=headers)
        if response.status_code == 201:
            return
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
            BaseModel: Валидированный объект модели.

        Raises:
            RuntimeError: Если ответ содержит ошибку.
            ValueError: Если валидация ответа не удалась.
        """
        print("from client.py",response.text)
        if response.status_code == 200:
            try:
                return model.model_validate(response.json(), by_alias=True)
            except ValidationError as e:
                raise ValueError(f"Ошибка валидации ответа: {e}")
        else:
            self._handle_error(response)

    def _handle_error(self, response: httpx.Response):
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
        except Exception:
            reason = response.text
        raise RuntimeError(f"API Ошибка {response.status_code}: {reason}")

    def close(self):
        """
        Закрывает HTTP клиент, освобождая ресурсы.
        """
        self.client.close()