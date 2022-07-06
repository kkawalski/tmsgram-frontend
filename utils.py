import requests

from flask import session


API_URL = "http://backend:8000/api"

def access_token_request(username, password):
    req = requests.post(f"{API_URL}/token/", json={
        "username": username,
        "password": password
    })
    req_data = req.json()
    return req_data


def refresh_token_request():
    refresh_token = session["refresh"]
    req = requests.post(f"{API_URL}/token/refresh/", json={
        "refresh": refresh_token
    })
    session["access"] = req.json()["access"]
    session.modified = True


def request_with_auth(
    method: str = None, url: str = None,
    headers: dict = None, files: dict = None,
    data: dict = None, json: dict = None,
    **kwargs,
) -> requests.Response:
    if headers is None:
        headers = {}

    access_token = session["access"]

    headers.update(Authorization=f"Bearer {access_token}")

    req = requests.Request(
        method=method, url=url,
        headers=headers, files=files,
        data=data, json=json,
        **kwargs
    )
    r = req.prepare()
    s = requests.Session()
    return s.send(r)


def request_with_refresh(
    method: str = None, url: str = None,
    headers: dict = None, files: dict = None,
    data: dict = None, json: dict = None,
    **kwargs,
) -> requests.Response:
    res = request_with_auth(
        method=method, url=url,
        headers=headers, files=files,
        data=data, json=json,
        **kwargs
    )
    if res.status_code == 403:
        refresh_token_request()
        res = request_with_auth(
            method=method, url=url,
            headers=headers, files=files,
            data=data, json=json,
            **kwargs
        )
    return res


def users_list_request():
    req = request_with_refresh("GET", f"{API_URL}/profiles/")
    req_data = req.json()
    return req_data

def user_retrieve_request(user_id):
    req = request_with_refresh("GET", f"{API_URL}/profiles/{user_id}")
    user_data = req.json()
    return user_data


def user_me_request():
    req = request_with_refresh("GET", f"{API_URL}/profiles/me/")
    user_data = req.json()
    return user_data


def post_list_request():
    req = request_with_refresh("GET", f"{API_URL}/posts/")
    posts_data = req.json()
    return posts_data

def post_create_request(description=None):
    req = request_with_refresh("POST", f"{API_URL}/posts/", json={
        "description": description
    })
    post_data = req.json()
    return post_data

def activate_user_request(register_token):
    req = requests.post(f"{API_URL}/profiles/activate/", json={
        "register_token": register_token
    })
    return True
