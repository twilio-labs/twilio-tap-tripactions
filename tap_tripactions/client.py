import requests, json

bookings_url = "https://api.tripactions.com/v1/bookings/"
token_url = "https://api.tripactions.com/ta-auth/oauth/token"
headers = {"content-type": "application/x-www-form-urlencoded"}


class OAuth2Client:
    def __init__(self, client_id, client_secret):
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.get_access_token()

    def get_access_token(self):
        data = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        self.access_token = requests.post(url=token_url, data=data, headers=headers).json()["access_token"]

    def get_booking_records(self, created_from, created_to, page, size=100):
        params = {"createdFrom": created_from, "createdTo": created_to, "page": page, "size": size}
        headers["Authorization"] = "Bearer " + self.access_token
        return requests.get(bookings_url, params=params, headers=headers)



