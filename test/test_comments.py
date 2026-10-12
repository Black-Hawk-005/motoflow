import uuid

import pytest

from test.helpers import (
    auth_headers,
    build_request,
    create_approved_customer,
    extra_mechanic,  # noqa: F401  (fixture)
    tracked_users,  # noqa: F401  (fixture; used by extra_mechanic)
)

MESSAGE = "Could you confirm the pickup time please?"


async def post_comment(client, headers, request_id, message=MESSAGE):
    return await client.post(
        "/comments/",
        json={"service_request_id": request_id, "message": message},
        headers=headers,
    )


async def get_comments(client, headers, request_id):
    return await client.get(
        "/comments/", params={"service_request_id": request_id}, headers=headers
    )


# --- posting ----------------------------------------------------------------


async def test_customer_comment_has_author_details(client):
    ctx = await build_request(client, "in_progress")

    response = await post_comment(client, ctx["customer_headers"], ctx["request_id"])

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == MESSAGE
    assert body["service_request_id"] == ctx["request_id"]
    assert body["author"]["id"] == ctx["customer"]["id"]
    assert body["author"]["role"] == "customer"
    assert body["author"]["full_name"] == ctx["customer"]["full_name"]
    assert "created_at" in body


async def test_assigned_mechanic_and_admin_can_comment(client):
    ctx = await build_request(client, "in_progress")

    mechanic = await post_comment(client, ctx["mechanic_headers"], ctx["request_id"])
    admin = await post_comment(client, ctx["admin_headers"], ctx["request_id"])

    assert mechanic.status_code == 201
    assert mechanic.json()["author"]["role"] == "mechanic"
    assert admin.status_code == 201
    assert admin.json()["author"]["role"] == "admin"


async def test_other_customer_cannot_comment_on_request(client):
    ctx = await build_request(client, "in_progress")
    intruder = await create_approved_customer(client)

    response = await post_comment(
        client, auth_headers(intruder["token"]), ctx["request_id"]
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No service request found"


async def test_unassigned_mechanic_cannot_comment_on_request(client, extra_mechanic):
    ctx = await build_request(client, "in_progress")

    response = await post_comment(client, extra_mechanic["headers"], ctx["request_id"])

    assert response.status_code == 404


async def test_comment_on_unknown_request_is_404(client):
    ctx = await build_request(client, "pending")

    response = await post_comment(client, ctx["customer_headers"], str(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "too short"},
        {"message": ""},
        {},
    ],
)
async def test_invalid_comment_payload_rejected(client, payload):
    ctx = await build_request(client, "pending")

    response = await client.post(
        "/comments/",
        json={"service_request_id": ctx["request_id"], **payload},
        headers=ctx["customer_headers"],
    )

    assert response.status_code == 422


async def test_comment_endpoints_require_authentication(client):
    request_id = str(uuid.uuid4())

    posted = await client.post(
        "/comments/", json={"service_request_id": request_id, "message": MESSAGE}
    )
    listed = await client.get("/comments/", params={"service_request_id": request_id})

    assert (posted.status_code, listed.status_code) == (401, 401)


# --- reading ----------------------------------------------------------------


async def test_thread_shows_every_authors_name_and_role(client):
    ctx = await build_request(client, "in_progress")
    await post_comment(client, ctx["customer_headers"], ctx["request_id"], "Customer says hello there")
    await post_comment(client, ctx["mechanic_headers"], ctx["request_id"], "Mechanic replies to customer")
    await post_comment(client, ctx["admin_headers"], ctx["request_id"], "Admin chimes in on this job")

    response = await get_comments(client, ctx["customer_headers"], ctx["request_id"])

    assert response.status_code == 200
    by_message = {c["message"]: c["author"] for c in response.json()}
    assert by_message["Customer says hello there"]["role"] == "customer"
    assert by_message["Mechanic replies to customer"]["role"] == "mechanic"
    assert by_message["Admin chimes in on this job"]["role"] == "admin"
    assert by_message["Customer says hello there"]["id"] == ctx["customer"]["id"]


async def test_thread_is_empty_for_a_new_request(client):
    ctx = await build_request(client, "pending")

    response = await get_comments(client, ctx["customer_headers"], ctx["request_id"])

    assert response.status_code == 200
    assert response.json() == []


async def test_comments_are_scoped_to_their_request(client):
    first = await build_request(client, "in_progress")
    second = await build_request(client, "in_progress")
    await post_comment(client, first["customer_headers"], first["request_id"], "Only visible on the first")

    response = await get_comments(client, second["customer_headers"], second["request_id"])

    assert response.json() == []


async def test_who_can_read_a_thread(client, extra_mechanic):
    ctx = await build_request(client, "in_progress")
    await post_comment(client, ctx["customer_headers"], ctx["request_id"])
    intruder = await create_approved_customer(client)

    allowed = [
        ctx["customer_headers"],
        ctx["mechanic_headers"],
        ctx["admin_headers"],
    ]
    for headers in allowed:
        response = await get_comments(client, headers, ctx["request_id"])
        assert response.status_code == 200
        assert len(response.json()) == 1

    for headers in (auth_headers(intruder["token"]), extra_mechanic["headers"]):
        response = await get_comments(client, headers, ctx["request_id"])
        assert response.status_code == 404


async def test_list_comments_unknown_request_and_missing_param(client):
    ctx = await build_request(client, "pending")

    unknown = await get_comments(client, ctx["customer_headers"], str(uuid.uuid4()))
    missing = await client.get("/comments/", headers=ctx["customer_headers"])

    assert unknown.status_code == 404
    assert missing.status_code == 422


# --- rejection note --------------------------------------------------------------


async def test_rejection_note_is_logged_as_the_customers_comment(client):
    ctx = await build_request(client, "action_required")
    note = "Quoted labour cost seems far too high"

    reject = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": note},
        headers=ctx["customer_headers"],
    )
    assert reject.status_code == 200

    for headers in (ctx["admin_headers"], ctx["mechanic_headers"]):
        thread = await get_comments(client, headers, ctx["request_id"])
        notes = [c for c in thread.json() if c["message"] == note]
        assert len(notes) == 1
        assert notes[0]["author"]["id"] == ctx["customer"]["id"]
        assert notes[0]["author"]["role"] == "customer"


async def test_failed_rejection_does_not_leave_a_comment_behind(client):
    ctx = await build_request(client, "in_progress")  # not action_required

    reject = await client.patch(
        f"/service-requests/{ctx['request_id']}/reject",
        json={"message": "Rejecting something that cannot be rejected"},
        headers=ctx["customer_headers"],
    )
    assert reject.status_code == 400

    thread = await get_comments(client, ctx["customer_headers"], ctx["request_id"])
    assert thread.json() == []
