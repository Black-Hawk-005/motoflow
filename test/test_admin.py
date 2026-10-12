import uuid

import pytest

from test.helpers import (
    auth_headers,
    build_payload,
    create_approved_customer,
    create_user_as_admin,
    get_admin_token,
    get_mechanic_token,
    login,
    register_user,
    tracked_users,  # noqa: F401  (fixture)
    unique_email,
    unique_phone,
)

# --- creating users -------------------------------------------------------


@pytest.mark.parametrize("role", ["customer", "mechanic", "admin"])
async def test_admin_creates_user_with_each_role(client, tracked_users, role):
    admin_token = await get_admin_token(client)

    response, payload = await create_user_as_admin(
        client, admin_token, tracked_users, role
    )

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == role
    assert body["email"] == payload["email"]
    assert body["is_approved"] is True
    assert "password" not in body
    assert "password_hash" not in body


async def test_user_created_by_admin_can_log_in_immediately(client, tracked_users):
    admin_token = await get_admin_token(client)
    _, payload = await create_user_as_admin(
        client, admin_token, tracked_users, "customer"
    )

    response = await client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_admin_created_admin_can_use_admin_endpoints(client, tracked_users):
    admin_token = await get_admin_token(client)
    _, payload = await create_user_as_admin(
        client, admin_token, tracked_users, "admin"
    )
    new_admin_token = await login(client, payload["email"], payload["password"])

    response = await client.get("/admin/users", headers=auth_headers(new_admin_token))

    assert response.status_code == 200


async def test_admin_cannot_create_duplicate_email(client, tracked_users):
    admin_token = await get_admin_token(client)
    _, first = await create_user_as_admin(client, admin_token, tracked_users, "customer")

    response, _ = await create_user_as_admin(
        client,
        admin_token,
        tracked_users,
        "customer",
        email=first["email"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


async def test_admin_cannot_create_duplicate_phone(client, tracked_users):
    admin_token = await get_admin_token(client)
    _, first = await create_user_as_admin(client, admin_token, tracked_users, "customer")

    response, _ = await create_user_as_admin(
        client,
        admin_token,
        tracked_users,
        "customer",
        phone=first["phone"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Phone number already registered"


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"phone": "12345"},
        {"phone": "not-a-phone"},
        {"email": "not-an-email"},
        {"full_name": "ab"},
    ],
)
async def test_admin_create_user_validation(client, tracked_users, overrides):
    admin_token = await get_admin_token(client)

    response, _ = await create_user_as_admin(
        client, admin_token, tracked_users, "customer", **overrides
    )

    assert response.status_code == 422


async def test_admin_cannot_create_user_with_unknown_role(client, tracked_users):
    admin_token = await get_admin_token(client)

    response, _ = await create_user_as_admin(
        client, admin_token, tracked_users, "superuser"
    )

    assert response.status_code == 422


# --- role gating ------------------------------------------------------------


async def test_non_admins_are_forbidden_from_admin_endpoints(client):
    customer = await create_approved_customer(client)
    mechanic_token = await get_mechanic_token(client)
    target = await register_user(client)

    for token in (customer["token"], mechanic_token):
        headers = auth_headers(token)
        create = await client.post(
            "/admin/users",
            json={
                "full_name": "Sneaky Person",
                "email": unique_email(),
                "password": "Str0ng-test-pass!",
                "phone": unique_phone(),
                "role": "admin",
            },
            headers=headers,
        )
        listing = await client.get("/admin/users", headers=headers)
        approve = await client.patch(
            f"/admin/users/{target['id']}/approve", headers=headers
        )
        assert (create.status_code, listing.status_code, approve.status_code) == (
            403,
            403,
            403,
        )


async def test_admin_endpoints_require_authentication(client):
    user_id = uuid.uuid4()

    responses = [
        await client.post("/admin/users", json={}),
        await client.get("/admin/users"),
        await client.patch(f"/admin/users/{user_id}/approve"),
    ]

    assert [r.status_code for r in responses] == [401, 401, 401]


async def test_non_admin_cannot_actually_approve_a_pending_user(client):
    pending = await register_user(client)
    customer = await create_approved_customer(client)

    await client.patch(
        f"/admin/users/{pending['id']}/approve",
        headers=auth_headers(customer["token"]),
    )

    response = await client.post(
        "/auth/login",
        data={"username": pending["email"], "password": pending["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Admin approval in process"


# --- listing and filtering ----------------------------------------------------


async def test_list_users_contains_seeded_staff_without_password_data(client):
    admin_token = await get_admin_token(client)

    response = await client.get("/admin/users", headers=auth_headers(admin_token))

    assert response.status_code == 200
    users = response.json()
    roles = {u["role"] for u in users}
    assert {"admin", "mechanic"} <= roles
    assert all("password_hash" not in u and "password" not in u for u in users)


async def test_list_users_filters_by_role(client):
    await register_user(client)
    admin_token = await get_admin_token(client)
    headers = auth_headers(admin_token)

    for role in ("customer", "mechanic", "admin"):
        response = await client.get("/admin/users", params={"role": role}, headers=headers)
        assert response.status_code == 200
        assert response.json(), f"expected at least one {role}"
        assert {u["role"] for u in response.json()} == {role}


async def test_list_users_filters_by_approval_state(client):
    pending = await register_user(client)
    admin_token = await get_admin_token(client)
    headers = auth_headers(admin_token)

    unapproved = await client.get(
        "/admin/users", params={"approval_state": "false"}, headers=headers
    )
    approved = await client.get(
        "/admin/users", params={"approval_state": "true"}, headers=headers
    )

    assert {u["is_approved"] for u in unapproved.json()} == {False}
    assert pending["id"] in {u["id"] for u in unapproved.json()}
    assert {u["is_approved"] for u in approved.json()} == {True}
    assert pending["id"] not in {u["id"] for u in approved.json()}


async def test_list_users_filters_by_role_and_approval_together(client):
    pending = await register_user(client)
    admin_token = await get_admin_token(client)

    response = await client.get(
        "/admin/users",
        params={"role": "customer", "approval_state": "false"},
        headers=auth_headers(admin_token),
    )

    users = response.json()
    assert pending["id"] in {u["id"] for u in users}
    assert {(u["role"], u["is_approved"]) for u in users} == {("customer", False)}


async def test_list_users_rejects_unknown_role_filter(client):
    admin_token = await get_admin_token(client)

    response = await client.get(
        "/admin/users", params={"role": "janitor"}, headers=auth_headers(admin_token)
    )

    assert response.status_code == 422


# --- approving users ----------------------------------------------------------


async def test_approve_user_flips_flag_and_is_idempotent(client):
    pending = await register_user(client)
    admin_token = await get_admin_token(client)
    headers = auth_headers(admin_token)

    first = await client.patch(f"/admin/users/{pending['id']}/approve", headers=headers)
    second = await client.patch(f"/admin/users/{pending['id']}/approve", headers=headers)

    assert first.status_code == 200
    assert first.json()["is_approved"] is True
    assert second.status_code == 200
    assert second.json()["is_approved"] is True


async def test_approve_unknown_user_is_404_and_bad_id_is_422(client):
    admin_token = await get_admin_token(client)
    headers = auth_headers(admin_token)

    missing = await client.patch(f"/admin/users/{uuid.uuid4()}/approve", headers=headers)
    malformed = await client.patch("/admin/users/not-a-uuid/approve", headers=headers)

    assert missing.status_code == 404
    assert malformed.status_code == 422


async def test_registration_ignores_client_supplied_role_and_approval(client):
    payload = build_payload()
    payload.update({"role": "admin", "is_approved": True})

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "customer"
    assert body["is_approved"] is False
