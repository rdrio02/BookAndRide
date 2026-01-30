import requests

API_BASE_URL = "http://nginx"


def login(email: str, password: str):
    response = requests.post(
        f"{API_BASE_URL}/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    print(response.text)
    response.raise_for_status()
    return response.json()


def register(email: str, password: str):
    response = requests.post(
        f"{API_BASE_URL}/register",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_me(token: str):
    response = requests.get(
        f"{API_BASE_URL}/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def start_rental(user_id: int, bike_id: str):
    r = requests.post(
        f"{API_BASE_URL}/rentals/start",
        json={"user_id": user_id, "bike_id": bike_id},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def stop_rental(rental_id: int):
    r = requests.post(
        f"{API_BASE_URL}/rentals/stop",
        json={"rental_id": rental_id},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()