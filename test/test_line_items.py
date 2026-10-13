import uuid
from decimal import Decimal
from test.helpers import extra_mechanic  # noqa: F401  (fixture)
from test.helpers import tracked_users  # noqa: F401  (fixture; used by extra_mechanic)
from test.helpers import (
    add_line_item,
    auth_headers,
    build_request,
    create_approved_customer,
    get_request_status,
)

import pytest

LOCKED_STATES = ["approved", "completed", "closed"]


def new_item(request_id, **overrides):
    payload = {
        "service_request_id": request_id,
        "description": "Replace the rear brake pads",
        "cost": "750.50",
    }
    payload.update(overrides)
    return payload


async def list_items(client, headers, request_id):
    return await client.get(
        "/line-items/", params={"service_request_id": request_id}, headers=headers
    )


# --- creating ---------------------------------------------------------------


async def test_assigned_mechanic_creates_line_item(client):
    ctx = await build_request(client, "in_progress", line_items=0)

    response = await client.post(
        "/line-items/",
        json=new_item(ctx["request_id"]),
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["service_request_id"] == ctx["request_id"]
    assert Decimal(body["cost"]) == Decimal("750.50")
    assert body["is_approved"] is False


async def test_only_mechanics_can_create_line_items(client):
    ctx = await build_request(client, "in_progress", line_items=0)
    payload = new_item(ctx["request_id"])

    customer = await client.post(
        "/line-items/", json=payload, headers=ctx["customer_headers"]
    )
    admin = await client.post(
        "/line-items/", json=payload, headers=ctx["admin_headers"]
    )
    anonymous = await client.post("/line-items/", json=payload)

    assert (customer.status_code, admin.status_code, anonymous.status_code) == (
        403,
        403,
        401,
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"description": "too short"},
        {"cost": "0"},
        {"cost": "-10.00"},
        {"cost": "free"},
    ],
)
async def test_invalid_line_item_payload_rejected(client, overrides):
    ctx = await build_request(client, "in_progress", line_items=0)

    response = await client.post(
        "/line-items/",
        json=new_item(ctx["request_id"], **overrides),
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 422


async def test_line_item_for_unknown_request_is_404(client):
    ctx = await build_request(client, "pending")

    response = await client.post(
        "/line-items/",
        json=new_item(str(uuid.uuid4())),
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 404


async def test_unassigned_mechanic_cannot_add_line_item(client, extra_mechanic):
    ctx = await build_request(client, "in_progress", line_items=0)

    response = await client.post(
        "/line-items/",
        json=new_item(ctx["request_id"]),
        headers=extra_mechanic["headers"],
    )

    assert response.status_code == 404


# --- the bill is locked once the request is approved/completed/closed ---------


@pytest.mark.parametrize("state", LOCKED_STATES)
async def test_line_items_are_locked_after_approval(client, state):
    ctx = await build_request(client, state, line_items=1)
    item_id = ctx["line_item_ids"][0]
    headers = ctx["mechanic_headers"]

    create = await client.post(
        "/line-items/", json=new_item(ctx["request_id"]), headers=headers
    )
    update = await client.patch(
        f"/line-items/{item_id}", json={"cost": "1.00"}, headers=headers
    )
    delete = await client.delete(f"/line-items/{item_id}", headers=headers)

    assert (create.status_code, update.status_code, delete.status_code) == (
        400,
        400,
        400,
    )
    items = (await list_items(client, ctx["admin_headers"], ctx["request_id"])).json()
    assert len(items) == 1
    assert Decimal(items[0]["cost"]) == Decimal("500.00")
    assert items[0]["is_approved"] is True


async def test_line_items_are_editable_while_action_required(client):
    ctx = await build_request(client, "action_required", line_items=1)

    response = await client.patch(
        f"/line-items/{ctx['line_item_ids'][0]}",
        json={"cost": "123.00"},
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 200
    assert Decimal(response.json()["cost"]) == Decimal("123.00")


async def test_line_items_unlock_again_when_request_is_reopened(client):
    ctx = await build_request(client, "approved", line_items=1)
    reopen = await client.patch(
        f"/service-requests/{ctx['request_id']}",
        json={"status": "in_progress"},
        headers=ctx["mechanic_headers"],
    )
    assert reopen.status_code == 200

    response = await client.post(
        "/line-items/",
        json=new_item(ctx["request_id"], description="Extra work found on reopening"),
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 201


# --- updating and deleting -----------------------------------------------------


async def test_editing_a_line_item_resets_its_approval(client):
    ctx = await build_request(client, "in_progress", line_items=1)
    item_id = ctx["line_item_ids"][0]
    approved = await client.patch(
        f"/line-items/{item_id}/approve", headers=ctx["customer_headers"]
    )
    assert approved.json()["is_approved"] is True

    response = await client.patch(
        f"/line-items/{item_id}",
        json={"description": "Replace the rear brake discs"},
        headers=ctx["mechanic_headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Replace the rear brake discs"
    assert response.json()["is_approved"] is False


async def test_update_validation_and_unknown_ids(client):
    ctx = await build_request(client, "in_progress", line_items=1)
    item_id = ctx["line_item_ids"][0]
    headers = ctx["mechanic_headers"]

    bad_cost = await client.patch(
        f"/line-items/{item_id}", json={"cost": "-5"}, headers=headers
    )
    bad_description = await client.patch(
        f"/line-items/{item_id}", json={"description": "short"}, headers=headers
    )
    missing = await client.patch(
        f"/line-items/{uuid.uuid4()}", json={"cost": "5"}, headers=headers
    )
    malformed = await client.patch(
        "/line-items/not-a-uuid", json={"cost": "5"}, headers=headers
    )

    assert bad_cost.status_code == 422
    assert bad_description.status_code == 422
    assert missing.status_code == 404
    assert malformed.status_code == 422


async def test_customer_and_admin_cannot_edit_or_delete_line_items(client):
    ctx = await build_request(client, "in_progress", line_items=1)
    item_id = ctx["line_item_ids"][0]

    for headers in (ctx["customer_headers"], ctx["admin_headers"]):
        update = await client.patch(
            f"/line-items/{item_id}", json={"cost": "1.00"}, headers=headers
        )
        delete = await client.delete(f"/line-items/{item_id}", headers=headers)
        assert (update.status_code, delete.status_code) == (403, 403)


async def test_other_mechanic_cannot_edit_or_delete_line_item(client, extra_mechanic):
    ctx = await build_request(client, "in_progress", line_items=1)
    item_id = ctx["line_item_ids"][0]

    update = await client.patch(
        f"/line-items/{item_id}",
        json={"cost": "1.00"},
        headers=extra_mechanic["headers"],
    )
    delete = await client.delete(
        f"/line-items/{item_id}", headers=extra_mechanic["headers"]
    )

    assert update.status_code == 404
    assert delete.status_code == 404
    items = (await list_items(client, ctx["admin_headers"], ctx["request_id"])).json()
    assert [Decimal(i["cost"]) for i in items] == [Decimal("500.00")]


async def test_mechanic_deletes_line_item(client):
    ctx = await build_request(client, "in_progress", line_items=2)
    doomed, kept = ctx["line_item_ids"]

    response = await client.delete(
        f"/line-items/{doomed}", headers=ctx["mechanic_headers"]
    )

    assert response.status_code == 204
    items = (await list_items(client, ctx["admin_headers"], ctx["request_id"])).json()
    assert [i["id"] for i in items] == [kept]


async def test_delete_unknown_line_item_is_404(client):
    ctx = await build_request(client, "in_progress", line_items=0)

    response = await client.delete(
        f"/line-items/{uuid.uuid4()}", headers=ctx["mechanic_headers"]
    )

    assert response.status_code == 404


# --- customer approval --------------------------------------------------------


async def test_customer_approves_own_line_item(client):
    ctx = await build_request(client, "action_required", line_items=1)

    response = await client.patch(
        f"/line-items/{ctx['line_item_ids'][0]}/approve",
        headers=ctx["customer_headers"],
    )

    assert response.status_code == 200
    assert response.json()["is_approved"] is True


async def test_other_customer_cannot_approve_line_item(client):
    ctx = await build_request(client, "action_required", line_items=1)
    intruder = await create_approved_customer(client)

    response = await client.patch(
        f"/line-items/{ctx['line_item_ids'][0]}/approve",
        headers=auth_headers(intruder["token"]),
    )

    assert response.status_code == 404
    items = (await list_items(client, ctx["admin_headers"], ctx["request_id"])).json()
    assert items[0]["is_approved"] is False


async def test_mechanic_and_admin_cannot_approve_line_items(client):
    ctx = await build_request(client, "action_required", line_items=1)
    item_id = ctx["line_item_ids"][0]

    for headers in (ctx["mechanic_headers"], ctx["admin_headers"]):
        response = await client.patch(f"/line-items/{item_id}/approve", headers=headers)
        assert response.status_code == 403


async def test_approve_unknown_line_item_is_404(client):
    customer = await create_approved_customer(client)

    response = await client.patch(
        f"/line-items/{uuid.uuid4()}/approve", headers=auth_headers(customer["token"])
    )

    assert response.status_code == 404


# --- request-level approval depends on every line item ------------------------


async def test_request_approval_needs_every_single_line_item_approved(client):
    ctx = await build_request(client, "action_required", line_items=2)
    first, second = ctx["line_item_ids"]
    approve_request = f"/service-requests/{ctx['request_id']}/approve"

    await client.patch(f"/line-items/{first}/approve", headers=ctx["customer_headers"])
    blocked = await client.patch(approve_request, headers=ctx["customer_headers"])
    assert blocked.status_code == 400
    assert blocked.json()["detail"] == "All line items are not approved"
    assert await get_request_status(client, ctx) == "action_required"

    await client.patch(f"/line-items/{second}/approve", headers=ctx["customer_headers"])
    allowed = await client.patch(approve_request, headers=ctx["customer_headers"])
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "approved"


async def test_editing_after_approving_items_blocks_request_approval_again(client):
    ctx = await build_request(client, "action_required", line_items=1)
    item_id = ctx["line_item_ids"][0]
    await client.patch(
        f"/line-items/{item_id}/approve", headers=ctx["customer_headers"]
    )

    edit = await client.patch(
        f"/line-items/{item_id}",
        json={"cost": "9999.00"},
        headers=ctx["mechanic_headers"],
    )
    assert edit.status_code == 200

    response = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )
    assert response.status_code == 400


async def test_new_line_item_added_before_approval_must_be_approved_too(client):
    ctx = await build_request(client, "action_required", line_items=1)
    await client.patch(
        f"/line-items/{ctx['line_item_ids'][0]}/approve",
        headers=ctx["customer_headers"],
    )
    await add_line_item(client, ctx["mechanic_token"], ctx["request_id"])

    response = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )

    assert response.status_code == 400


# --- listing -----------------------------------------------------------------


async def test_customer_mechanic_and_admin_can_list_a_requests_line_items(client):
    ctx = await build_request(client, "in_progress", line_items=2)

    for headers in (
        ctx["customer_headers"],
        ctx["mechanic_headers"],
        ctx["admin_headers"],
    ):
        response = await list_items(client, headers, ctx["request_id"])
        assert response.status_code == 200
        assert {i["id"] for i in response.json()} == set(ctx["line_item_ids"])


async def test_other_customer_cannot_list_line_items(client):
    ctx = await build_request(client, "in_progress", line_items=1)
    intruder = await create_approved_customer(client)

    response = await list_items(
        client, auth_headers(intruder["token"]), ctx["request_id"]
    )

    assert response.status_code == 404


async def test_list_line_items_unknown_request_and_missing_param(client):
    customer = await create_approved_customer(client)
    headers = auth_headers(customer["token"])

    unknown = await list_items(client, headers, str(uuid.uuid4()))
    missing = await client.get("/line-items/", headers=headers)

    assert unknown.status_code == 404
    assert missing.status_code == 422


async def test_line_item_endpoints_require_authentication(client):
    item_id = uuid.uuid4()

    responses = [
        await client.get("/line-items/", params={"service_request_id": str(item_id)}),
        await client.post("/line-items/", json=new_item(str(item_id))),
        await client.patch(f"/line-items/{item_id}", json={"cost": "5"}),
        await client.patch(f"/line-items/{item_id}/approve"),
        await client.delete(f"/line-items/{item_id}"),
    ]

    assert [r.status_code for r in responses] == [401] * 5


async def test_unassigned_mechanic_cannot_list_line_items(client, extra_mechanic):
    ctx = await build_request(client, "in_progress", line_items=1)

    response = await list_items(client, extra_mechanic["headers"], ctx["request_id"])

    assert response.status_code == 404
