import random
from datetime import datetime, timedelta, timezone


def generate_otp():
    return str(random.randint(100000, 999999))


def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=5)