import httpx

from src.api.client import BookerClient
from src.api.models import Booking, AuthRequest, AuthResponse
from src.api.routes import Routes
from src.config import settings


def main():
    booking_data = {
            "firstname": "Bob",
            "lastname": "Simpson",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2024-06-01",
                "checkout": "2024-06-10"
            },
            "additionalneeds": "Breakfast"
        }
    data = Booking(**booking_data)
    client = BookerClient()
    # client.get_booking(Routes.booking_by_id(9101))

    #get token
    res = AuthRequest(username=settings.user_name, password=settings.password)
    r = httpx.Client().post("https://restful-booker.herokuapp.com/auth", json=res.model_dump(by_alias=True))
    AuthResponse.model_validate(r.json(), by_alias=True)






if __name__ == "__main__":
    main()