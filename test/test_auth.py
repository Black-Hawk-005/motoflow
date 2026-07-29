import random


def build_payload(**overrides):
    unique_id = random.randint(100000, 999999)
    payload = {
        "full_name": "Nikhilesh H",
        "email": f"nikgrinding{unique_id}@gmail.com",
        "password": "nik@12323",
        "phone": f"+9194029{unique_id}",
    }
    payload.update(overrides)
    return payload


async def register_user(client, **overrides):
    payload = build_payload(**overrides)
    response = await client.post("/auth/register", json=payload)
    return {**payload, "id": response.json()["id"]}


ADMIN_EMAIL = "admin@motoflow.co.in"
ADMIN_PASSWORD = "admin@123"


async def get_admin_token(client):
    response = await client.post(
        "/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    return response.json()["access_token"]


async def test_register_success(client):
    payload = build_payload()
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == payload["email"]
    assert body["role"] == "customer"
    assert "password" not in body
    assert "password_hash" not in body


async def test_duplicate_email_register_fail(client):
    user = await register_user(client)

    response = await client.post(
        "/auth/register",
        json=build_payload(email=user["email"]),
    )

    assert response.status_code == 400


async def test_duplicate_phone_register_fail(client):
    user = await register_user(client)

    response = await client.post(
        "/auth/register",
        json=build_payload(phone=user["phone"]),
    )

    assert response.status_code == 400


async def test_user_login_with_invalid_email(client):
    response = await client.post(
        "/auth/login",
        data={
            "username": build_payload()["email"],
            "password": "nik@12323",
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Check your request and try again"


async def test_user_login_with_invalid_password(client):
    user = await register_user(client)

    response = await client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": "wrong-password-123",
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Check your request and try again"


async def test_user_login_with_pending_approval(client):
    user = await register_user(client)

    response = await client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Admin approval in process"


async def test_login_success(client):
    response = await client.post(
        "/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body   
    assert body["token_type"] == "bearer"


async def test_register_then_admin_approve_then_login_succeeds(client):
    user = await register_user(client)

    blocked_response = await client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert blocked_response.status_code == 401

    admin_token = await get_admin_token(client)

    approve_response = await client.patch(
        f"/admin/users/{user['id']}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
