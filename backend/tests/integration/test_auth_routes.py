import uuid

import pytest

from Utilities import User_Authentication as legacy_auth


@pytest.fixture
def test_username():
    username = f"pytest_{uuid.uuid4().hex[:10]}"
    yield username
    legacy_auth.users.delete_one({"username": username})


async def test_register_login_me_flow(client, test_username):
    register_res = await client.post(
        "/api/v1/auth/register",
        json={
            "username": test_username,
            "password": "password123",
            "confirm_password": "password123",
            "email": f"{test_username}@example.com",
        },
    )
    assert register_res.status_code == 200
    assert register_res.json()["message"] == "User registered successfully!"

    login_res = await client.post(
        "/api/v1/auth/login", json={"username": test_username, "password": "password123"}
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me_res = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["username"] == test_username


async def test_login_wrong_password_returns_401(client, test_username):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": test_username,
            "password": "password123",
            "confirm_password": "password123",
            "email": f"{test_username}@example.com",
        },
    )
    res = await client.post(
        "/api/v1/auth/login", json={"username": test_username, "password": "wrong-password"}
    )
    assert res.status_code == 401


async def test_me_requires_auth(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


async def test_register_is_rate_limited(client, test_username):
    payload = {
        "username": test_username,
        "password": "password123",
        "confirm_password": "password123",
        "email": f"{test_username}@example.com",
    }
    responses = [await client.post("/api/v1/auth/register", json=payload) for _ in range(6)]
    statuses = [r.status_code for r in responses]
    assert 429 in statuses  # 6th call exceeds the 5/minute limit
    assert statuses.count(200) <= 1  # only the first registration should ever succeed


async def test_register_duplicate_username_rejected(client, test_username):
    payload = {
        "username": test_username,
        "password": "password123",
        "confirm_password": "password123",
        "email": f"{test_username}@example.com",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200
    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400
