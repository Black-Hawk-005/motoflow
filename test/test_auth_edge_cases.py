import uuid
from datetime import timedelta

import jwt
import pytest

from app.auth import create_access_token
from app.config import settings
from test.helpers import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    auth_headers,
    build_payload,
    create_approved_customer,
    get_admin_token,
    get_mechanic_token,
    register_user,
    unique_plate,
)

WRONG_KEY = "this-is-definitely-not-the-real-signing-key-0123456789"


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


# --- /auth/me and token validation ---------------------------------------------


async def test_me_returns_the_current_user(client):
    customer = await create_approved_customer(client)

    response = await client.get("/auth/me", headers=bearer(customer["token"]))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == customer["id"]
    assert body["email"] == customer["email"]
    assert body["role"] == "customer"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "GET /auth/me has no response_model and returns the ORM user, so the "
        "argon2 password_hash is included in the JSON response"
    ),
)
async def test_me_does_not_leak_password_hash(client):
    customer = await create_approved_customer(client)

    response = await client.get("/auth/me", headers=bearer(customer["token"]))

    assert response.status_code == 200
    assert "password_hash" not in response.json()
    assert "password" not in response.json()


async def test_me_requires_a_token(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401


def _crafted_tokens():
    sub = str(uuid.uuid4())
    key = settings.secret_key.get_secret_value()
    return {
        "garbage": "not.a.jwt",
        "expired": create_access_token({"sub": sub}, expires_delta=timedelta(minutes=-5)),
        "wrong signing key": jwt.encode(
            {"sub": sub, "exp": 4102444800}, WRONG_KEY, algorithm="HS256"
        ),
        "missing exp claim": jwt.encode({"sub": sub}, key, algorithm="HS256"),
        "missing sub claim": jwt.encode({"exp": 4102444800}, key, algorithm="HS256"),
        "sub is not a uuid": create_access_token({"sub": "not-a-uuid"}),
        "user does not exist": create_access_token({"sub": sub}),
        "alg none": jwt.encode({"sub": sub, "exp": 4102444800}, None, algorithm="none"),
    }


@pytest.mark.parametrize("kind", list(_crafted_tokens().keys()))
async def test_invalid_tokens_are_rejected_with_401(client, kind):
    token = _crafted_tokens()[kind]

    response = await client.get("/auth/me", headers=bearer(token))

    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


async def test_non_bearer_authorization_scheme_is_rejected(client):
    customer = await create_approved_customer(client)

    response = await client.get(
        "/auth/me", headers={"Authorization": f"Basic {customer['token']}"}
    )

    assert response.status_code == 401


async def test_token_is_tied_to_the_user_not_to_a_role_claim(client):
    """A customer token carrying a forged 'admin' role claim gains nothing."""
    customer = await create_approved_customer(client)
    forged = create_access_token({"sub": customer["id"], "role": "admin"})

    response = await client.get("/admin/users", headers=bearer(forged))

    assert response.status_code == 403


# --- login edge cases -----------------------------------------------------------


async def test_wrong_password_for_approved_user_is_401(client):
    response = await client.post(
        "/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD + "x"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Check your request and try again"


async def test_wrong_password_for_unapproved_user_does_not_reveal_pending_state(client):
    user = await register_user(client)

    response = await client.post(
        "/auth/login",
        data={"username": user["email"], "password": "definitely-wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Check your request and try again"


async def test_login_expects_form_data_not_json(client):
    response = await client.post(
        "/auth/login",
        json={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )

    assert response.status_code == 422


async def test_login_with_missing_fields_is_422(client):
    response = await client.post("/auth/login", data={"username": ADMIN_EMAIL})

    assert response.status_code == 422


async def test_login_token_contains_user_id_and_role(client):
    admin_token = await get_admin_token(client)

    claims = jwt.decode(
        admin_token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
    )

    assert claims["role"] == "admin"
    assert uuid.UUID(claims["sub"])
    assert "exp" in claims


# --- registration validation ----------------------------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"email": "not-an-email"},
        {"phone": "12345"},
        {"phone": "abcdefghij"},
        {"full_name": "ab"},
    ],
)
async def test_register_validation_errors(client, overrides):
    response = await client.post("/auth/register", json=build_payload(**overrides))

    assert response.status_code == 422


async def test_register_requires_all_fields(client):
    response = await client.post("/auth/register", json={"email": "someone@gmail.com"})

    assert response.status_code == 422


async def test_registered_user_starts_unapproved_customer(client):
    payload = build_payload()

    response = await client.post("/auth/register", json=payload)

    body = response.json()
    assert body["role"] == "customer"
    assert body["is_approved"] is False


# --- role gating across routers -------------------------------------------------


async def test_role_restricted_endpoints_return_403_for_wrong_role(client):
    customer = await create_approved_customer(client)
    mechanic_token = await get_mechanic_token(client)
    admin_token = await get_admin_token(client)
    fake_id = str(uuid.uuid4())

    # mechanic-only: creating line items
    line_item = {
        "service_request_id": fake_id,
        "description": "Replace the front brake discs",
        "cost": "100.00",
    }
    for token in (customer["token"], admin_token):
        response = await client.post(
            "/line-items/", json=line_item, headers=auth_headers(token)
        )
        assert response.status_code == 403

    # customer-only: creating service requests
    request = {"vehicle_id": fake_id, "initial_complaint": "Strange noise from the engine"}
    for token in (mechanic_token, admin_token):
        response = await client.post(
            "/service-requests/", json=request, headers=auth_headers(token)
        )
        assert response.status_code == 403

    # customer-only: approving and rejecting requests
    for token in (mechanic_token, admin_token):
        approve = await client.patch(
            f"/service-requests/{fake_id}/approve", headers=auth_headers(token)
        )
        reject = await client.patch(
            f"/service-requests/{fake_id}/reject",
            json={"message": "nope"},
            headers=auth_headers(token),
        )
        assert approve.status_code == 403
        assert reject.status_code == 403

    # staff-only: updating requests
    response = await client.patch(
        f"/service-requests/{fake_id}",
        json={"status": "assigned"},
        headers=auth_headers(customer["token"]),
    )
    assert response.status_code == 403

    # vehicles cannot be created by mechanics
    response = await client.post(
        "/vehicles/",
        json={
            "make": "Maruti Suzuki",
            "model": "Swift",
            "year": 2020,
            "license_plate": unique_plate(),
        },
        headers=auth_headers(mechanic_token),
    )
    assert response.status_code == 403
