import random


async def test_register_success(client):
    unique_id = random.randint(100000, 999999)
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Nikhilesh H",
            "email": f"nikgrinding{unique_id}@gmail.com",
            "password": "nik@12323",
            "phone": f"+9194029{unique_id}",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == f"nikgrinding{unique_id}@gmail.com"
    assert body["role"] == "customer"
    assert "password" not in body
    assert "password_hash" not in body
