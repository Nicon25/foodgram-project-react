import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == "me":
        raise ValidationError(
            ("Юзернейм не может быть <me>."),
            params={"value": value},
        )
    if re.search(r"^[\w.@+-]+$", value) is None:
        raise ValidationError(
            (f"Не допустимые символы <{value}> в юзернейме."),
            params={"value": value},
        )
