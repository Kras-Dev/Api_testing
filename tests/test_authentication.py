#tests/test_authentication.py
import allure
import pytest

from src.api.routes import Routes
from src.config import settings


@allure.feature("Authentication")
class TestAuthentication:
    @allure.title("Успешная аутентификация")
    def test_auth_success(self, client):
        """
        Проверяет успешную аутентификацию с корректными данными.

        Проверяет, что возвращается валидный токен в виде непустой строки.
        """
        with allure.step("Аутентификация с корректными данными"):
            token = client.authenticate(settings.user_name, settings.password, Routes.AUTH).token
        assert isinstance(token, str)
        assert len(token) > 0

    @allure.title("Ошибка аутентификации с некорректными данными")
    @pytest.mark.parametrize("username,password", [
        ("wronguser", "password123"),
        ("admin", "wrongpassword"),
        ("", ""),
    ])
    def test_auth_failure(self, client, username, password):
        """
        Проверяет, что при неверных данных аутентификация завершается ошибкой.

        Ожидается выброс RuntimeError с сообщением об ошибке авторизации.
        """
        with allure.step(f"Аутентификация с некорректными данными: {username}/{password}"):
            with pytest.raises(RuntimeError) as exc_info:
                client.authenticate(username, password, Routes.AUTH)
        error_msg = str(exc_info.value).lower()
        assert ("401" in error_msg) or ("api ошибка" in error_msg) or ("bad credentials" in error_msg)
