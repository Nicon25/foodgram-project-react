import re

from django.core.exceptions import ValidationError
# from django.utils import timezone


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Юзернейм не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[\w.@+-]+\z', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в юзернейме.'),
            params={'value': value},
        )


# def validate_year(value):
#     now = timezone.now().year
#     if value > now:
#         raise ValidationError(
#             f'{value} не может быть больше {now}'
#         )
