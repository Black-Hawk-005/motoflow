import uuid

import pytest

from test.helpers import (
    auth_headers,
    build_request,
    create_approved_customer,
    get_admin_token,
    get_mechanic_id,
    get_mechanic_token,
    vehicle_payload,
)


async def add_vehicle(client, token, **overrides):
    payload = vehicle_payload(**overrides)
    response = await client.post(
        "/vehicles/", json=payload, headers=auth_headers(token)
    )
    return response, payload


# --- create ---------------------------------------------------------------


async def test_customer_adds_vehicle(client):
    customer = await create_approved_customer(client)

    response, payload = await add_vehicle(client, customer["token"])

    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer["id"]
    assert body["make"] == payload["make"]
    assert body["license_plate"] == payload["license_plate"]


async def test_duplicate_license_plate_rejected(client):
    first = await create_approved_customer(client)
    second = await create_approved_customer(client)
    _, payload = await add_vehicle(client, first["token"])

    response = await client.post(
        "/vehicles/", json=payload, headers=auth_headers(second["token"])
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Vehicle already registered"


@pytest.mark.parametrize(
    "overrides",
    [
        {"license_plate": "KA01"},
        {"year": 1885},
        {"year": 1800},
        {"year": "not-a-year"},
        {"make": ""},
    ],
)
async def test_invalid_vehicle_payload_rejected(client, overrides):
    customer = await create_approved_customer(client)

    response, _ = await add_vehicle(client, customer["token"], **overrides)

    assert response.status_code == 422


async def test_missing_vehicle_fields_rejected(client):
    customer = await create_approved_customer(client)

    response = await client.post(
        "/vehicles/",
        json={"make": "Maruti Suzuki"},
        headers=auth_headers(customer["token"]),
    )

    assert response.status_code == 422


@pytest.mark.xfail(
    strict=True,
    reason=(
        "VehicleCreate uses min_length=4 for make/model, so common real values "
        "such as 'BMW', 'Kia', 'i20' or 'X5' are rejected with 422"
    ),
)
@pytest.mark.parametrize(
    "overrides",
    [{"make": "BMW"}, {"make": "Kia"}, {"model": "i20"}, {"model": "X5"}],
)
async def test_short_real_world_make_and_model_names_accepted(client, overrides):
    customer = await create_approved_customer(client)

    response, _ = await add_vehicle(client, customer["token"], **overrides)

    assert response.status_code == 201


async def test_mechanic_cannot_add_vehicle(client):
    token = await get_mechanic_token(client)

    response, _ = await add_vehicle(client, token)

    assert response.status_code == 403


async def test_customer_cannot_register_vehicle_for_someone_else(client):
    me = await create_approved_customer(client)
    other = await create_approved_customer(client)

    response = await client.post(
        "/vehicles/",
        params={"customer_id": other["id"]},
        json=vehicle_payload(),
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == me["id"]


async def test_admin_adds_vehicle_for_a_customer(client):
    customer = await create_approved_customer(client)
    admin_token = await get_admin_token(client)

    response = await client.post(
        "/vehicles/",
        params={"customer_id": customer["id"]},
        json=vehicle_payload(),
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == customer["id"]


async def test_admin_must_name_the_customer(client):
    admin_token = await get_admin_token(client)

    response = await client.post(
        "/vehicles/", json=vehicle_payload(), headers=auth_headers(admin_token)
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Customer-ID required"


async def test_admin_cannot_assign_vehicle_to_unknown_or_non_customer(client):
    admin_token = await get_admin_token(client)
    mechanic_id = await get_mechanic_id(client, admin_token)

    for customer_id in (str(uuid.uuid4()), mechanic_id):
        response = await client.post(
            "/vehicles/",
            params={"customer_id": customer_id},
            json=vehicle_payload(),
            headers=auth_headers(admin_token),
        )
        assert response.status_code == 404


async def test_vehicle_endpoints_require_authentication(client):
    vehicle_id = str(uuid.uuid4())

    responses = [
        await client.post("/vehicles/", json=vehicle_payload()),
        await client.get("/vehicles/"),
        await client.get(f"/vehicles/{vehicle_id}"),
        await client.patch(f"/vehicles/{vehicle_id}", json={"year": 2021}),
        await client.delete(f"/vehicles/{vehicle_id}"),
    ]

    assert [r.status_code for r in responses] == [401] * 5


# --- read -----------------------------------------------------------------


async def test_customer_lists_only_own_vehicles(client):
    me = await create_approved_customer(client)
    other = await create_approved_customer(client)
    mine, _ = await add_vehicle(client, me["token"])
    theirs, _ = await add_vehicle(client, other["token"])

    response = await client.get("/vehicles/", headers=auth_headers(me["token"]))

    assert response.status_code == 200
    ids = {v["id"] for v in response.json()}
    assert mine.json()["id"] in ids
    assert theirs.json()["id"] not in ids
    assert {v["customer_id"] for v in response.json()} == {me["id"]}


async def test_admin_lists_every_customers_vehicles(client):
    first = await create_approved_customer(client)
    second = await create_approved_customer(client)
    one, _ = await add_vehicle(client, first["token"])
    two, _ = await add_vehicle(client, second["token"])
    admin_token = await get_admin_token(client)

    response = await client.get("/vehicles/", headers=auth_headers(admin_token))

    assert response.status_code == 200
    ids = {v["id"] for v in response.json()}
    assert {one.json()["id"], two.json()["id"]} <= ids


async def test_customer_gets_own_vehicle(client):
    me = await create_approved_customer(client)
    created, _ = await add_vehicle(client, me["token"])

    response = await client.get(
        f"/vehicles/{created.json()['id']}", headers=auth_headers(me["token"])
    )

    assert response.status_code == 200
    assert response.json()["id"] == created.json()["id"]


async def test_other_customers_vehicle_is_404_not_403(client):
    owner = await create_approved_customer(client)
    intruder = await create_approved_customer(client)
    created, _ = await add_vehicle(client, owner["token"])

    response = await client.get(
        f"/vehicles/{created.json()['id']}", headers=auth_headers(intruder["token"])
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


async def test_unknown_vehicle_is_404_and_bad_id_is_422(client):
    customer = await create_approved_customer(client)
    headers = auth_headers(customer["token"])

    missing = await client.get(f"/vehicles/{uuid.uuid4()}", headers=headers)
    malformed = await client.get("/vehicles/not-a-uuid", headers=headers)

    assert missing.status_code == 404
    assert malformed.status_code == 422


async def test_admin_can_read_any_vehicle(client):
    owner = await create_approved_customer(client)
    created, _ = await add_vehicle(client, owner["token"])
    admin_token = await get_admin_token(client)

    response = await client.get(
        f"/vehicles/{created.json()['id']}", headers=auth_headers(admin_token)
    )

    assert response.status_code == 200


# --- update ---------------------------------------------------------------


async def test_owner_updates_vehicle_partially(client):
    me = await create_approved_customer(client)
    created, payload = await add_vehicle(client, me["token"])

    response = await client.patch(
        f"/vehicles/{created.json()['id']}",
        json={"year": 2022},
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["year"] == 2022
    assert body["make"] == payload["make"]
    assert body["license_plate"] == payload["license_plate"]


async def test_owner_can_resubmit_own_license_plate(client):
    me = await create_approved_customer(client)
    created, payload = await add_vehicle(client, me["token"])

    response = await client.patch(
        f"/vehicles/{created.json()['id']}",
        json={"license_plate": payload["license_plate"]},
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 200


async def test_update_to_a_taken_license_plate_rejected(client):
    me = await create_approved_customer(client)
    first, _ = await add_vehicle(client, me["token"])
    second, _ = await add_vehicle(client, me["token"])

    response = await client.patch(
        f"/vehicles/{second.json()['id']}",
        json={"license_plate": first.json()["license_plate"]},
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "License plate already registered"


async def test_update_validation(client):
    me = await create_approved_customer(client)
    created, _ = await add_vehicle(client, me["token"])

    response = await client.patch(
        f"/vehicles/{created.json()['id']}",
        json={"year": 1700},
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 422


async def test_cannot_update_another_customers_vehicle(client):
    owner = await create_approved_customer(client)
    intruder = await create_approved_customer(client)
    created, payload = await add_vehicle(client, owner["token"])
    vehicle_id = created.json()["id"]

    response = await client.patch(
        f"/vehicles/{vehicle_id}",
        json={"year": 1999},
        headers=auth_headers(intruder["token"]),
    )

    assert response.status_code == 404
    unchanged = await client.get(
        f"/vehicles/{vehicle_id}", headers=auth_headers(owner["token"])
    )
    assert unchanged.json()["year"] == payload["year"]


async def test_update_unknown_vehicle_is_404(client):
    me = await create_approved_customer(client)

    response = await client.patch(
        f"/vehicles/{uuid.uuid4()}",
        json={"year": 2021},
        headers=auth_headers(me["token"]),
    )

    assert response.status_code == 404


# --- delete ---------------------------------------------------------------


async def test_owner_deletes_vehicle(client):
    me = await create_approved_customer(client)
    created, _ = await add_vehicle(client, me["token"])
    vehicle_id = created.json()["id"]

    response = await client.delete(
        f"/vehicles/{vehicle_id}", headers=auth_headers(me["token"])
    )
    assert response.status_code == 204

    after = await client.get(
        f"/vehicles/{vehicle_id}", headers=auth_headers(me["token"])
    )
    assert after.status_code == 404


async def test_cannot_delete_another_customers_vehicle(client):
    owner = await create_approved_customer(client)
    intruder = await create_approved_customer(client)
    created, _ = await add_vehicle(client, owner["token"])
    vehicle_id = created.json()["id"]

    response = await client.delete(
        f"/vehicles/{vehicle_id}", headers=auth_headers(intruder["token"])
    )
    assert response.status_code == 404

    still_there = await client.get(
        f"/vehicles/{vehicle_id}", headers=auth_headers(owner["token"])
    )
    assert still_there.status_code == 200


async def test_delete_unknown_vehicle_is_404(client):
    me = await create_approved_customer(client)

    response = await client.delete(
        f"/vehicles/{uuid.uuid4()}", headers=auth_headers(me["token"])
    )

    assert response.status_code == 404


@pytest.mark.xfail(
    strict=True,
    reason=(
        "service_requests.vehicle_id has no ON DELETE rule, so deleting a "
        "vehicle that has a service request raises an IntegrityError (HTTP 500) "
        "instead of a clean 4xx response"
    ),
)
async def test_deleting_vehicle_with_service_request_returns_client_error(client):
    ctx = await build_request(client, "pending")

    response = await client.delete(
        f"/vehicles/{ctx['vehicle']['id']}", headers=ctx["customer_headers"]
    )

    assert response.status_code in (400, 409)
