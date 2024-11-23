
import random
import string


def session_id_generator(pk, min_length=10, max_length=20):
    seed = "SESSION"

    length = random.randint(min_length, max_length)
    value = ''.join(random.choices(string.ascii_uppercase, k=length))
    return f'{seed}-{pk}-{value}'