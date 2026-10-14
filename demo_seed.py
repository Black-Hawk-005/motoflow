"""Seed demo data (customers, vehicles, service requests in every status).

Needs the admin/mechanic accounts from admin_mech_seed.py to exist first.
DEMO_CUSTOMER_PASSWORD is the login password for the demo customer account.
Safe to re-run: does nothing if the demo customer already exists.
"""

import asyncio
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select

from app import models
from app.auth import hash_password
from app.database import AsyncSessionLocal
from app.schemas import ServiceStatus as S
from app.schemas import UserRole

DEMO_CUSTOMER_EMAIL = "customer@motoflow.dev"
SECOND_CUSTOMER_EMAIL = "meera@motoflow.dev"
SECOND_MECHANIC_EMAIL = "priya@motoflow.dev"

# (customer index, vehicle index, mechanic index or None, status, days ago,
#  complaint, [(line item, cost, approved)], [(author, message)])
# customers: 0 = demo customer, 1 = second customer
# mechanics: 0 = seeded mechanic, 1 = second mechanic
# comment author: "c" = request's customer, "m" = request's mechanic
REQUESTS = [
    (0, 0, None, S.PENDING, 1,
     "Engine makes a rattling noise when idling, mostly in the morning.",
     [], []),
    (0, 1, 0, S.ASSIGNED, 2,
     "Brakes feel spongy and the rear brake squeals.",
     [], [("m", "Got it, bring the bike in any time before 5 pm.")]),
    (1, 2, 0, S.IN_PROGRESS, 3,
     "AC is not cooling properly and there is a burning smell.",
     [("Replace AC compressor belt", "3500.00", False),
      ("Refrigerant refill", "2200.00", False)],
     [("m", "Belt is cracked. I am drafting the estimate now.")]),
    (0, 0, 0, S.ACTION_REQUIRED, 5,
     "Regular 40,000 km service.",
     [("Engine oil and filter change", "1800.00", True),
      ("Air filter replacement", "650.00", False),
      ("Front brake pad replacement", "2400.00", False)],
     [("m", "Brake pads are worn below 3 mm, so I recommend replacing them."),
      ("c", "Thanks. Can you confirm the pads are original-spec?")]),
    (1, 3, 0, S.APPROVED, 7,
     "Chain is loose and makes noise at low speed.",
     [("Chain and sprocket adjustment", "900.00", True),
      ("Chain lubrication", "250.00", True)],
     [("m", "Estimate sent for approval."),
      ("c", "Approved, please go ahead.")]),
    (0, 1, 1, S.CLOSED, 21,
     "Annual service and headlight bulb replaced.",
     [("General service", "1500.00", True),
      ("Headlight bulb", "450.00", True)],
     [("m", "All done. The bike is ready for pickup."),
      ("c", "Picked up, thank you!")]),
]


def new_user(role, name, email, phone, password):
    return models.User(
        role=role,
        full_name=name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
    )


async def get_user(db, email):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().one_or_none()


async def main():
    password = os.environ.get("DEMO_CUSTOMER_PASSWORD")
    if not password:
        sys.exit("Set DEMO_CUSTOMER_PASSWORD first.")
    mechanic_email = os.environ.get("SEED_MECHANIC_EMAIL", "mechanic@motoflow.dev")

    async with AsyncSessionLocal() as db:
        if await get_user(db, DEMO_CUSTOMER_EMAIL):
            print("Demo data already present, nothing to do.")
            return

        mechanic = await get_user(db, mechanic_email)
        if not mechanic:
            sys.exit("Seeded mechanic not found. Run admin_mech_seed.py first.")

        # The second customer/mechanic exist only to fill the lists; nobody logs
        # in as them, so they get random throwaway passwords.
        customers = [
            new_user(UserRole.CUSTOMER, "Aarav Sharma", DEMO_CUSTOMER_EMAIL,
                     "9876543210", password),
            new_user(UserRole.CUSTOMER, "Meera Iyer", SECOND_CUSTOMER_EMAIL,
                     "9876501234", secrets.token_urlsafe(24)),
        ]
        mechanic2 = new_user(UserRole.MECHANIC, "Priya Nair", SECOND_MECHANIC_EMAIL,
                             "9876505678", secrets.token_urlsafe(24))
        mechanics = [mechanic, mechanic2]
        db.add_all([*customers, mechanic2])
        await db.flush()

        vehicle_specs = [
            (0, "Honda", "City", 2019, "KA01AB1234"),
            (0, "Royal Enfield", "Classic 350", 2021, "KA05MN4521"),
            (1, "Hyundai", "i20", 2020, "TN09CD7788"),
            (1, "Suzuki", "Access 125", 2022, "TN10XY3321"),
        ]
        vehicles = [
            models.Vehicle(
                customer_id=customers[c].id,
                make=make,
                model=model,
                year=year,
                license_plate=plate,
            )
            for c, make, model, year, plate in vehicle_specs
        ]
        db.add_all(vehicles)
        await db.flush()

        now = datetime.now(timezone.utc)
        for c, v, m, status, days, complaint, items, comments in REQUESTS:
            created = now - timedelta(days=days)
            sr = models.ServiceRequest(
                customer_id=customers[c].id,
                vehicle_id=vehicles[v].id,
                mechanic_id=mechanics[m].id if m is not None else None,
                initial_complaint=complaint,
                status=status,
                created_at=created,
                updated_at=created + timedelta(hours=6),
            )
            db.add(sr)
            await db.flush()
            for description, cost, approved in items:
                db.add(
                    models.ServiceLineItem(
                        service_request_id=sr.id,
                        description=description,
                        cost=Decimal(cost),
                        is_approved=approved,
                    )
                )
            for n, (who, message) in enumerate(comments, start=1):
                author = customers[c] if who == "c" else mechanics[m]
                db.add(
                    models.Comment(
                        service_request_id=sr.id,
                        author_id=author.id,
                        message=message,
                        created_at=created + timedelta(hours=n),
                    )
                )

        await db.commit()
        print(f"Added {len(REQUESTS)} demo service requests.")


if __name__ == "__main__":
    asyncio.run(main())
