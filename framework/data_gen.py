from __future__ import annotations

import random
import string
from dataclasses import dataclass

from faker import Faker

fake = Faker()


def rand_string(min_len: int = 5, max_len: int = 15) -> str:
    n = random.randint(min_len, max_len)
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def rand_int(min_v: int = 0, max_v: int = 10_000) -> int:
    return random.randint(min_v, max_v)


@dataclass(frozen=True)
class UserPayload:
    name: str
    email: str
    city: str
    user_id: int

    def as_dict(self) -> dict:
        return {"name": self.name, "email": self.email, "city": self.city, "user_id": self.user_id}


def make_user_payload() -> UserPayload:
    return UserPayload(
        name=fake.name(),
        email=fake.email(),
        city=fake.city(),
        user_id=rand_int(1, 10_000_000),
    )
