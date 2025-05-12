#tests/test_authentication.py
import allure
import pytest

from src.config import settings


@allure.feature("Authentication")
class TestAuthentication:
    @allure.title("Успешная аутентификация")
    def test_auth_success(self, client, get_auth_token):
        token = get_auth_token
        assert isinstance(token, str)
        assert len(token) > 0

    # @allure.title("Ошибка аутентификации с неверными данными")
    # @pytest.mark.parametrize("username,password", [
    #     ("wronguser", "password123"),
    #     ("admin", "wrongpassword"),
    #     ("", ""),
    # ])
    # def test_auth_failure(self, client, username, password):
    #     with pytest.raises(RuntimeError) as excinfo:
    #         client.authenticate(username, password)
    #     assert "401" in str(excinfo.value) or "API ошибка" in str(excinfo.value)