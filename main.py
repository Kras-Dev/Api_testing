#main.py

import random
from src.api.client import BookerClient
from src.api.models import Booking
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

    booking_data_v2 = {
            "firstname": "Bob",
            "lastname": "Brown",
            "totalprice": 0,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2024-07-15",
                "checkout": "2024-07-20"
            },
            "additionalneeds": None
        }

    data = Booking(**booking_data)
    client = BookerClient()
    # client.get_booking(Routes.booking_by_id(9101))

    #get token
    a_r = client.authenticate(user_name=settings.user_name, password=settings.password, route="https://restful-booker.herokuapp.com/auth")
    print(f"a_R: {a_r}, type: {type(a_r)}")

    #get ids
    g_ids = client.get_booking_ids(Routes.BOOKING)
    random_booking = random.choice(g_ids).booking_id
    print("ids: ", len(g_ids), "ran: ", random_booking, " ", type(random_booking))

    #create booking
    cr_c = client.create_booking(data, Routes.BOOKING)
    print("cr_c:", cr_c.model_dump_json(indent=3))

    #getbooking
    g_b = client.get_booking(Routes.booking_by_id(random_booking))
    print("gb:", g_b.model_dump_json(indent=3))

    #update booking
    u_b = client.update_booking(Booking(**booking_data_v2),Routes.booking_by_id(random_booking), a_r.token)
    print("u_b: ",u_b.model_dump_json(indent=3))

    #delete booking
    d_b = client.delete_booking(Routes.booking_by_id(random_booking), a_r.token)
    print("del booking: ", d_b)

if __name__ == "__main__":
    main()