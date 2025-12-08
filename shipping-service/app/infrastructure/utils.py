import random
import string


def generate_ship_code(prefix: str = "SHIP-") -> str:
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{prefix}{letters}{numbers}"