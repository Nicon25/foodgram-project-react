import re

from django.core.exceptions import ValidationError


def validate_slug(value):
    if re.search(r"^[-a-zA-Z0-9_]+$", value) is None:
        raise ValidationError(
            (f"The characters <{value}> are not allowed in the slug."),
            params={"value": value},
        )
