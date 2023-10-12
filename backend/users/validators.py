import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == "me":
        raise ValidationError(
            ("The username cannot be <me>."),
            params={"value": value},
        )
    if re.search(r"^[\w.@+-]+$", value) is None:
        raise ValidationError(
            (f"The characters <{value}> are not allowed in the username."),
            params={"value": value},
        )
