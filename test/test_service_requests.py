import random
from test.test_auth import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    get_admin_token,
    register_user,
)


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def login(client, email, password):
    response = await client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


async def create_approved_customer(client):
    user = await register_user(client)
    admin_token = await get_admin_token(client)
    await client.patch(
        f"/admin/users/{user['id']}/approve",
        headers=auth_headers(admin_token),
    )
    token = await login(client, user["email"], user["password"])
    return {**user, "token": token}


async def create_vehicle(client, customer_token, **overrides):
    unique_id = random.randint(100000, 999999)
    payload = {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "year": 2020,
        "license_plate": f"KA05AB{unique_id}",
    }
    payload.update(overrides)
    response = await client.post(
        "/vehicles/",
        json=payload,
        headers=auth_headers(customer_token),
    )
    return response.json()


async def create_service_request(client, customer_token, vehicle_id):
    response = await client.post(
        "/service-requests/",
        json={
            "vehicle_id": vehicle_id,
            "initial_complaint": "Engine making a rattling noise on startup.",
        },
        headers=auth_headers(customer_token),
    )
    return response.json()


async def get_seeded_mechanic_id(client, admin_token):
    response = await client.get(
        "/admin/users",
        params={"role": "mechanic"},
        headers=auth_headers(admin_token),
    )
    return response.json()[0]["id"]


MECHANIC_EMAIL = "mech202606@motoflow.co.in"
MECHANIC_PASSWORD = "mech@123"


async def get_mechanic_token(client):
    return await login(client, MECHANIC_EMAIL, MECHANIC_PASSWORD)


async def advance_to_action_required(client):
    """Arrange a service request through pending -> assigned -> in_progress -> action_required, with one unapproved line item attached, ready for the
    approve/reject tests to act on."""
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    service_request = await create_service_request(
        client, customer["token"], vehicle["id"]
    )

    admin_token = await get_admin_token(client)
    mechanic_id = await get_seeded_mechanic_id(client, admin_token)
    mechanic_token = await get_mechanic_token(client)

    await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "assigned", "mechanic_id": mechanic_id},
        headers=auth_headers(admin_token),
    )
    await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "in_progress"},
        headers=auth_headers(mechanic_token),
    )

    line_item_response = await client.post(
        "/line-items/",
        json={
            "service_request_id": service_request["id"],
            "description": "Clutch assembly replacement",
            "cost": "6500.00",
        },
        headers=auth_headers(mechanic_token),
    )
    line_item = line_item_response.json()

    await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "action_required"},
        headers=auth_headers(mechanic_token),
    )

    return {
        "customer": customer,
        "admin_token": admin_token,
        "mechanic_token": mechanic_token,
        "service_request_id": service_request["id"],
        "line_item_id": line_item["id"],
    }


async def test_assign_without_mechanic_fails(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    service_request = await create_service_request(
        client, customer["token"], vehicle["id"]
    )

    admin_token = await get_admin_token(client)
    response = await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "assigned"},
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot mark as assigned without a mechanic"


async def test_invalid_transition_pending_to_completed_fails(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    service_request = await create_service_request(
        client, customer["token"], vehicle["id"]
    )

    admin_token = await get_admin_token(client)
    response = await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "completed"},
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status change"


async def test_assign_with_mechanic_succeeds(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    service_request = await create_service_request(
        client, customer["token"], vehicle["id"]
    )

    admin_token = await get_admin_token(client)
    mechanic_id = await get_seeded_mechanic_id(client, admin_token)

    response = await client.patch(
        f"/service-requests/{service_request['id']}",
        json={"status": "assigned", "mechanic_id": mechanic_id},
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "assigned"
    assert body["mechanic_id"] == mechanic_id


async def test_approve_blocked_until_line_items_approved(client):
    ctx = await advance_to_action_required(client)
    customer_headers = auth_headers(ctx["customer"]["token"])

    blocked_response = await client.patch(
        f"/service-requests/{ctx['service_request_id']}/approve",
        headers=customer_headers,
    )
    assert blocked_response.status_code == 400
    assert blocked_response.json()["detail"] == "All line items are not approved"

    approve_item_response = await client.patch(
        f"/line-items/{ctx['line_item_id']}/approve",
        headers=customer_headers,
    )
    assert approve_item_response.status_code == 200

    approve_sr_response = await client.patch(
        f"/service-requests/{ctx['service_request_id']}/approve",
        headers=customer_headers,
    )
    assert approve_sr_response.status_code == 200
    assert approve_sr_response.json()["status"] == "approved"


async def test_reject_returns_to_in_progress_with_comment(client):
    ctx = await advance_to_action_required(client)
    customer_headers = auth_headers(ctx["customer"]["token"])
    rejection_message = "The quoted cost seems too high, please review."

    reject_response = await client.patch(
        f"/service-requests/{ctx['service_request_id']}/reject",
        json={"message": rejection_message},
        headers=customer_headers,
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "in_progress"

    comments_response = await client.get(
        "/comments/",
        params={"service_request_id": ctx["service_request_id"]},
        headers=customer_headers,
    )
    messages = [c["message"] for c in comments_response.json()]
    assert rejection_message in messages


async def test_full_happy_path_to_closed(client):
    ctx = await advance_to_action_required(client)
    customer_headers = auth_headers(ctx["customer"]["token"])
    mechanic_headers = auth_headers(ctx["mechanic_token"])

    await client.patch(
        f"/line-items/{ctx['line_item_id']}/approve",
        headers=customer_headers,
    )
    await client.patch(
        f"/service-requests/{ctx['service_request_id']}/approve",
        headers=customer_headers,
    )

    completed_response = await client.patch(
        f"/service-requests/{ctx['service_request_id']}",
        json={"status": "completed"},
        headers=mechanic_headers,
    )
    assert completed_response.status_code == 200
    assert completed_response.json()["status"] == "completed"

    closed_response = await client.patch(
        f"/service-requests/{ctx['service_request_id']}",
        json={"status": "closed"},
        headers=mechanic_headers,
    )
    assert closed_response.status_code == 200
    assert closed_response.json()["status"] == "closed"
