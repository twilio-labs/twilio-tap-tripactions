import unittest
from tap_tripactions import client
import json
from datetime import datetime



class TestClient(unittest.TestCase):
    with open("./test/secrets/secret_tripactions.json") as f:
        secret = json.load(f)
    client_id = secret['client_id']
    client_secret = secret["client_secret"]

    def test_get_auth_token(self):
        trip_action_client = client.OAuth2Client(client_id=self.client_id, client_secret=self.client_secret)
        self.assertTrue(trip_action_client.access_token is not None)

    def test_get_booking_records(self):
        trip_action_client = client.OAuth2Client(client_id=self.client_id, client_secret=self.client_secret)
        result = trip_action_client.get_booking_records(created_from=1534181486, created_to=1619174892, page=0, size=2)
        print(json.dumps(result.json()['data']))
        self.assertTrue(result)

    def test_pagination(self):
        trip_action_client = client.OAuth2Client(client_id=self.client_id, client_secret=self.client_secret)
        result = trip_action_client.get_booking_records(created_from=1534181486, created_to=1534760177, page=0, size=100)
        num_pages = result.json()['page']['totalPages']
        for page in range(0, num_pages+1):
            result = trip_action_client.get_booking_records(created_from=1534181486, created_to=1534760177, page=page,
                                                            size=100)
            print(page)

        self.assertEqual(num_pages, 2)


