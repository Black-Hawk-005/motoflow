import uuid

import pytest

from test.helpers import (
    STATUS_ORDER,
    auth_headers,
    build_request,
    create_approved_customer,
    create_service_request,
    create_vehicle,
    extra_mechanic,  # noqa: F401  (fixture)
    get_admin_token,
    get_request_status,
    patch_request,
    tracked_users,  # noqa: F401  (fixture; used by extra_mechanic)
)

# Statuses reachable from each state through PATCH /service-requests/{id}
# (approve/reject have their own endpoints and are tested separately).
ALLOWED_PATCH = {
    "pending": {"assigned"},
    "assigned": {"in_progress"},
    "in_progress": {"action_required"},
    "action_required": set(),
    "approved": {"completed", "in_progress"},
    "completed": {"closed"},
    "closed": set(),
}


# --- the state machine --------------------------------------------------------


@pytest.mark.parametrize("state", STATUS_ORDER)
async def test_every_invalid_transition_is_rejected(client, state):
    ctx = await build_request(client, state)
    staff = {"admin": ctx["admin_token"], "mechanic": ctx["mechanic_token"]}

    for target in STATUS_ORDER:
        if target in ALLOWED_PATCH[state]:
            continue
        body = {"status": target}
        if target == "assigned":
            body["mechanic_id"] = ctx["mechanic_id"]
        for who, token in staff.items():
            if who == "mechanic" and "mechanic_id" in body:
                continue  # covered by the admin-only assignment test
            response = await patch_request(client, token, ctx["request_id"], **body)
            assert response.status_code == 400, (
                f"{who}: {state} -> {target} should be rejected, got "
                f"{response.status_code}"
            )
    assert await get_request_status(client, ctx) == state


async def test_unknown_status_value_is_rejected(client):
    ctx = await build_request(client, "pending")

    response = await patch_request(
        client, ctx["admin_token"], ctx["request_id"], status="teleported"
    )

    assert response.status_code == 422


async def test_job_cannot_skip_customer_approval(client):
    ctx = await build_request(client, "action_required")

    for target in ("approved", "completed", "closed"):
        for token in (ctx["mechanic_token"], ctx["admin_token"]):
            response = await patch_request(
                client, token, ctx["request_id"], status=target
            )
            assert response.status_code == 400
    assert await get_request_status(client, ctx) == "action_required"


async def test_closed_is_terminal(client):
    ctx = await build_request(client, "closed")

    for target in STATUS_ORDER:
        response = await patch_request(
            client, ctx["admin_token"], ctx["request_id"], status=target
        )
        assert response.status_code == 400
    assert await get_request_status(client, ctx) == "closed"


# --- reopening an approved request -----------------------------------------------


async def test_approved_request_can_be_reopened_and_must_earn_approval_again(client):
    ctx = await build_request(client, "approved", line_items=1)

    reopened = await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], status="in_progress"
    )
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "in_progress"

    # no shortcut straight back to approved/completed
    for target in ("approved", "completed"):
        shortcut = await patch_request(
            client, ctx["mechanic_token"], ctx["request_id"], status=target
        )
        assert shortcut.status_code == 400
    direct_approve = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )
    assert direct_approve.status_code == 400

    # it has to go through action_required and customer approval again
    back = await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], status="action_required"
    )
    assert back.status_code == 200
    final = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )
    assert final.status_code == 200
    assert final.json()["status"] == "approved"


async def test_new_work_added_while_reopened_needs_fresh_approval(client):
    ctx = await build_request(client, "approved", line_items=1)
    await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], status="in_progress"
    )
    extra = await client.post(
        "/line-items/",
        json={
            "service_request_id": ctx["request_id"],
            "description": "Extra coolant hose replacement",
            "cost": "300.00",
        },
        headers=ctx["mechanic_headers"],
    )
    assert extra.status_code == 201
    await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], status="action_required"
    )

    blocked = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )
    assert blocked.status_code == 400

    await client.patch(
        f"/line-items/{extra.json()['id']}/approve", headers=ctx["customer_headers"]
    )
    allowed = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve",
        headers=ctx["customer_headers"],
    )
    assert allowed.status_code == 200


# --- rejecting ------------------------------------------------------------------


async def test_rejected_request_returns_to_in_progress_and_can_be_resubmitted(client):
    ctx = await build_request(client, "action_required")

    reject = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": "Please explain the second line item"},
        headers=ctx["customer_headers"],
    )
    assert reject.status_code == 200
    assert reject.json()["status"] == "in_progress"

    again = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": "Rejecting a second time in a row"},
        headers=ctx["customer_headers"],
    )
    assert again.status_code == 400

    resubmit = await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], status="action_required"
    )
    assert resubmit.status_code == 200


@pytest.mark.parametrize("state", ["pending", "assigned", "in_progress", "approved"])
async def test_reject_and_approve_only_work_from_action_required(client, state):
    ctx = await build_request(client, state)
    headers = ctx["customer_headers"]

    reject = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": "Trying to reject at the wrong time"},
        headers=headers,
    )
    approve = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve", headers=headers
    )

    assert (reject.status_code, approve.status_code) == (400, 400)
    assert await get_request_status(client, ctx) == state


async def test_other_customer_cannot_approve_or_reject(client):
    ctx = await build_request(client, "action_required")
    intruder = auth_headers((await create_approved_customer(client))["token"])

    approve = await client.patch(
        f"/service-requests/{ctx['request_id']}/approve", headers=intruder
    )
    reject = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": "Not my request but rejecting it"},
        headers=intruder,
    )

    assert (approve.status_code, reject.status_code) == (404, 404)
    assert await get_request_status(client, ctx) == "action_required"


async def test_approve_and_reject_unknown_request_are_404(client):
    customer = await create_approved_customer(client)
    headers = auth_headers(customer["token"])

    approve = await client.patch(
        f"/service-requests/{uuid.uuid4()}/approve", headers=headers
    )
    reject = await client.patch(
        f"/service-requests/{uuid.uuid4()}/reject",
        json={"message": "Rejecting a request that is not there"},
        headers=headers,
    )

    assert (approve.status_code, reject.status_code) == (404, 404)


async def test_reject_requires_a_message_field(client):
    ctx = await build_request(client, "action_required")

    response = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={},
        headers=ctx["customer_headers"],
    )

    assert response.status_code == 422
    assert await get_request_status(client, ctx) == "action_required"


@pytest.mark.parametrize("message", ["", "   "])
async def test_reject_requires_a_non_blank_note(client, message):
    ctx = await build_request(client, "action_required")

    response = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": message},
        headers=ctx["customer_headers"],
    )

    assert response.status_code == 422


# --- assigning a mechanic ---------------------------------------------------------


async def test_only_admins_can_assign_a_mechanic(client):
    ctx = await build_request(client, "pending")

    response = await patch_request(
        client,
        ctx["mechanic_token"],
        ctx["request_id"],
        status="assigned",
        mechanic_id=ctx["mechanic_id"],
    )

    assert response.status_code == 403
    assert await get_request_status(client, ctx) == "pending"


async def test_assignment_needs_a_real_mechanic(client):
    ctx = await build_request(client, "pending")
    customer_id = ctx["customer"]["id"]

    for bad_id in (str(uuid.uuid4()), customer_id):
        response = await patch_request(
            client,
            ctx["admin_token"],
            ctx["request_id"],
            status="assigned",
            mechanic_id=bad_id,
        )
        assert response.status_code == 400
    assert await get_request_status(client, ctx) == "pending"


async def test_assigning_a_pending_request_must_also_set_status_assigned(client):
    ctx = await build_request(client, "pending")

    response = await patch_request(
        client, ctx["admin_token"], ctx["request_id"], mechanic_id=ctx["mechanic_id"]
    )

    assert response.status_code == 400
    assert await get_request_status(client, ctx) == "pending"


async def test_null_mechanic_id_is_rejected(client):
    ctx = await build_request(client, "pending")

    response = await patch_request(
        client,
        ctx["admin_token"],
        ctx["request_id"],
        status="assigned",
        mechanic_id=None,
    )

    assert response.status_code == 400


async def test_null_mechanic_id_cannot_unassign_a_started_request(client):
    ctx = await build_request(client, "in_progress")

    as_admin = await patch_request(
        client, ctx["admin_token"], ctx["request_id"], mechanic_id=None
    )
    as_mechanic = await patch_request(
        client, ctx["mechanic_token"], ctx["request_id"], mechanic_id=None
    )

    assert as_admin.status_code == 400
    assert as_mechanic.status_code == 403
    current = await client.get(
        f"/service-requests/{ctx['request_id']}", headers=ctx["admin_headers"]
    )
    assert current.json()["mechanic_id"] == ctx["mechanic_id"]


async def test_update_unknown_request_is_404(client):
    admin_token = await get_admin_token(client)

    response = await patch_request(
        client, admin_token, str(uuid.uuid4()), status="assigned"
    )

    assert response.status_code == 404


async def test_unassigned_mechanic_cannot_change_request_status(client, extra_mechanic):
    ctx = await build_request(client, "assigned")

    response = await patch_request(
        client, extra_mechanic["token"], ctx["request_id"], status="in_progress"
    )

    assert response.status_code == 404
    assert await get_request_status(client, ctx) == "assigned"


# --- creating and reading requests -----------------------------------------------


async def test_customer_creates_request_with_pending_status(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])

    response = await client.post(
        "/service-requests/",
        json={
            "vehicle_id": vehicle["id"],
            "initial_complaint": "Brakes are squealing loudly",
        },
        headers=auth_headers(customer["token"]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["mechanic_id"] is None
    assert body["customer_id"] == customer["id"]
    assert body["vehicle_id"] == vehicle["id"]


async def test_cannot_open_request_for_someone_elses_or_unknown_vehicle(client):
    owner = await create_approved_customer(client)
    other = await create_approved_customer(client)
    vehicle = await create_vehicle(client, owner["token"])
    headers = auth_headers(other["token"])

    for vehicle_id in (vehicle["id"], str(uuid.uuid4())):
        response = await client.post(
            "/service-requests/",
            json={
                "vehicle_id": vehicle_id,
                "initial_complaint": "Brakes are squealing loudly",
            },
            headers=headers,
        )
        assert response.status_code == 404


async def test_service_request_validation(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    headers = auth_headers(customer["token"])

    short = await client.post(
        "/service-requests/",
        json={"vehicle_id": vehicle["id"], "initial_complaint": "noise"},
        headers=headers,
    )
    bad_id = await client.post(
        "/service-requests/",
        json={"vehicle_id": "nope", "initial_complaint": "Brakes are squealing loudly"},
        headers=headers,
    )

    assert short.status_code == 422
    assert bad_id.status_code == 422


async def test_request_endpoints_require_authentication(client):
    request_id = uuid.uuid4()

    responses = [
        await client.post("/service-requests/", json={}),
        await client.get("/service-requests/"),
        await client.get(f"/service-requests/{request_id}"),
        await client.patch(f"/service-requests/{request_id}", json={}),
        await client.patch(f"/service-requests/{request_id}/approve"),
        await client.patch(
            f"/service-requests/{request_id}/reject", json={"message": "x"}
        ),
    ]

    assert [r.status_code for r in responses] == [401] * 6


async def test_customers_only_see_their_own_requests(client):
    mine = await build_request(client, "pending")
    theirs = await build_request(client, "pending")

    listing = await client.get("/service-requests/", headers=mine["customer_headers"])
    detail = await client.get(
        f"/service-requests/{theirs['request_id']}", headers=mine["customer_headers"]
    )

    ids = {r["id"] for r in listing.json()}
    assert mine["request_id"] in ids
    assert theirs["request_id"] not in ids
    assert detail.status_code == 404


async def test_mechanic_only_sees_assigned_requests(client, extra_mechanic):
    assigned = await build_request(client, "assigned")
    unassigned = await build_request(client, "pending")

    listing = await client.get(
        "/service-requests/", headers=assigned["mechanic_headers"]
    )
    ids = {r["id"] for r in listing.json()}
    assert assigned["request_id"] in ids
    assert unassigned["request_id"] not in ids

    own = await client.get(
        f"/service-requests/{assigned['request_id']}", headers=extra_mechanic["headers"]
    )
    other = await client.get(
        f"/service-requests/{unassigned['request_id']}",
        headers=assigned["mechanic_headers"],
    )
    assert own.status_code == 404
    assert other.status_code == 404


async def test_admin_sees_every_request(client):
    first = await build_request(client, "pending")
    second = await build_request(client, "assigned")

    listing = await client.get("/service-requests/", headers=first["admin_headers"])

    ids = {r["id"] for r in listing.json()}
    assert {first["request_id"], second["request_id"]} <= ids


async def test_detail_exposes_contact_and_mechanic_info_by_role(client):
    ctx = await build_request(client, "assigned")
    url = f"/service-requests/{ctx['request_id']}"

    as_customer = (await client.get(url, headers=ctx["customer_headers"])).json()
    as_mechanic = (await client.get(url, headers=ctx["mechanic_headers"])).json()
    as_admin = (await client.get(url, headers=ctx["admin_headers"])).json()

    assert as_customer["customer"] is None
    assert as_customer["mechanic"]["id"] == ctx["mechanic_id"]
    for staff_view in (as_mechanic, as_admin):
        assert staff_view["customer"]["id"] == ctx["customer"]["id"]
        assert staff_view["customer"]["email"] == ctx["customer"]["email"]
        assert staff_view["mechanic"]["id"] == ctx["mechanic_id"]


async def test_customer_cannot_update_request_status(client):
    ctx = await build_request(client, "pending")

    response = await patch_request(
        client, ctx["customer"]["token"], ctx["request_id"], status="assigned"
    )

    assert response.status_code == 403


async def test_multiple_requests_for_same_vehicle_are_independent(client):
    customer = await create_approved_customer(client)
    vehicle = await create_vehicle(client, customer["token"])
    first = await create_service_request(client, customer["token"], vehicle["id"])
    second = await create_service_request(client, customer["token"], vehicle["id"])
    admin_token = await get_admin_token(client)

    assert first["id"] != second["id"]
    assert first["status"] == second["status"] == "pending"
    response = await patch_request(client, admin_token, first["id"], status="completed")
    assert response.status_code == 400
    listing = await client.get(
        "/service-requests/", headers=auth_headers(customer["token"])
    )
    assert {first["id"], second["id"]} <= {r["id"] for r in listing.json()}
