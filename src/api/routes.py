#src/api/routes.py

class Routes:
    """
    Класс, содержащий константы и методы для формирования URL маршрутов API.
    """
    AUTH = "/auth"
    BOOKING = "/booking"

    @staticmethod
    def booking_by_id(booking_id: int) -> str:
        """
        Формирует путь для доступа к конкретному бронированию по его ID.

        Args:
           booking_id (int): Уникальный идентификатор бронирования.

        Returns:
           str: Относительный URL путь для доступа к бронированию.
        """
        return f"/booking/{booking_id}"