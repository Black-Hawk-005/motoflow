"""Shared helpers and fixtures for the extended test-suite.

Everything here talks to the API through the same `client` fixture as the
existing tests and only ever touches the database configured in `.env.test`.
Not collected by pytest (the file name does not start with `test_`).
"""

import uuid

import pytest
from sqlalchemy import delete

from app import models
from test.conftest import AsyncSessionLocal
from test.test_auth import (  # noqa: F401
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    build_payload,
    get_admin_token,
    register_user,
)
from test.test_service_requests import (  # noqa: F401
    MECHANIC_EMAIL,
    MECHANIC_PASSWORD,
    auth_headers,
    create_approved_customer,
    create_service_request,
    create_vehicle,
    get_mechanic_token,
    login,
)

STATUS_ORDER = [
    "pending",
    "assigned",
    "in_progress",
    "action_required",
    "approved",
    "completed",
    "closed",
]


def unique_email(prefix="t"):
    return f"{prefix}{uuid.uuid4().hex[:12]}@gmail.com"


def unique_phone():
    return f"+91{10**9 + uuid.uuid4().int % (9 * 10**9)}"


def unique_plate():
    return f"KA09TS{uuid.uuid4().hex[:10].upper()}"


def vehicle_payload(**overrides):
    payload = {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "year": 2020,
        "license_plate": unique_plate(),
    }
    payload.update(overrides)
    return payload


async def get_mechanic_id(client, admin_token):
    """Id of the *seeded* mechanic (not just the first mechanic returned)."""
    response = await client.get(
        "/admin/users",
        params={"role": "mechanic"},
        headers=auth_headers(admin_token),
    )
    for user in response.json():
        if user["email"] == MECHANIC_EMAIL:
            return user["id"]
    raise AssertionError("seeded mechanic not found in the test database")


async def patch_request(client, token, request_id, **body):
    return await client.patch(
        f"/service-requests/{request_id}",
        json=body,
        headers=auth_headers(token),
    )


async def add_line_item(
    client, mechanic_token, request_id, description="Brake pad replacement", cost="900.00"
):
    response = await client.post(
        "/line-items/",
        json={
            "service_request_id": request_id,
            "description": description,
            "cost": cost,
        },
        headers=auth_headers(mechanic_token),
    )
    assert response.status_code == 201, response.text
    return response.json()


async def build_request(client, target="pending", line_items=1):
    """Create a customer, vehicle and service request and walk it forward.

    `target` is one of STATUS_ORDER. For every state from `in_progress`
    onwards `line_items` items are added by the assigned (seeded) mechanic,
    and they are approved by the customer on the way to `approved`.
    Returns a dict with everything a test needs.
    """
    index = STATUS_ORDER.index(target)

    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    service_request = await create_service_request(
        client, customer["token"], vehicle["id"]
    )
    request_id = service_request["id"]

    admin_token = await get_admin_token(client)
    mechanic_id = await get_mechanic_id(client, admin_token)
    mechanic_token = await get_mechanic_token(client)

    ctx = {
        "customer": customer,
        "customer_headers": auth_headers(customer["token"]),
        "vehicle": vehicle,
        "request_id": request_id,
        "admin_token": admin_token,
        "admin_headers": auth_headers(admin_token),
        "mechanic_id": mechanic_id,
        "mechanic_token": mechanic_token,
        "mechanic_headers": auth_headers(mechanic_token),
        "line_item_ids": [],
    }

    if index >= 1:
        response = await patch_request(
            client,
            admin_token,
            request_id,
            status="assigned",
            mechanic_id=mechanic_id,
        )
        assert response.status_code == 200, response.text
    if index >= 2:
        response = await patch_request(
            client, mechanic_token, request_id, status="in_progress"
        )
        assert response.status_code == 200, response.text
        for number in range(line_items):
            item = await add_line_item(
                client,
                mechanic_token,
                request_id,
                description=f"Service work item number {number + 1}",
                cost=f"{(number + 1) * 500}.00",
            )
            ctx["line_item_ids"].append(item["id"])
    if index >= 3:
        response = await patch_request(
            client, mechanic_token, request_id, status="action_required"
        )
        assert response.status_code == 200, response.text
    if index >= 4:
        for item_id in ctx["line_item_ids"]:
            response = await client.patch(
                f"/line-items/{item_id}/approve", headers=ctx["customer_headers"]
            )
            assert response.status_code == 200, response.text
        response = await client.patch(
            f"/service-requests/{request_id}/approve",
            headers=ctx["customer_headers"],
        )
        assert response.status_code == 200, response.text
    if index >= 5:
        response = await patch_request(
            client, mechanic_token, request_id, status="completed"
        )
        assert response.status_code == 200, response.text
    if index >= 6:
        response = await patch_request(
            client, mechanic_token, request_id, status="closed"
        )
        assert response.status_code == 200, response.text

    return ctx


async def get_request_status(client, ctx):
    response = await client.get(
        f"/service-requests/{ctx['request_id']}", headers=ctx["admin_headers"]
    )
    assert response.status_code == 200, response.text
    return response.json()["status"]


# --- users created through the admin API (removed again after each test) ----


@pytest.fixture()
async def tracked_users():
    """Collects emails of users a test creates and deletes them afterwards.

    The rest of the suite assumes exactly one mechanic and one admin exist, so
    tests that create staff accounts must clean up after themselves. Only the
    local test database (see conftest.py) is touched.
    """
    emails = []
    yield emails
    if emails:
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(models.User).where(models.User.email.in_(emails))
            )
            await session.commit()


async def create_user_as_admin(client, admin_token, tracked, role, **overrides):
    payload = {
        "full_name": "Extra Staff Member",
        "email": unique_email("staff"),
        "password": "Str0ng-test-pass!",
        "phone": unique_phone(),
        "role": role,
    }
    payload.update(overrides)
    tracked.append(payload["email"])
    response = await client.post(
        "/admin/users", json=payload, headers=auth_headers(admin_token)
    )
    return response, payload


@pytest.fixture()
async def extra_mechanic(client, tracked_users):
    """A second, throw-away mechanic with a ready-to-use token."""
    admin_token = await get_admin_token(client)
    response, payload = await create_user_as_admin(
        client, admin_token, tracked_users, "mechanic"
    )
    assert response.status_code == 201, response.text
    token = await login(client, payload["email"], payload["password"])
    return {
        "id": response.json()["id"],
        "email": payload["email"],
        "token": token,
        "headers": auth_headers(token),
    }
