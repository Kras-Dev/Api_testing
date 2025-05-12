#src/api/routes.py

class Routes:
    AUTH = "/auth"
    BOOKING = "/booking"

    @staticmethod
    def booking_by_id(booking_id: int) -> str:
        return f"/booking/{booking_id}"