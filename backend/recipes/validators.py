import datetime as dt
import re

from django.core.exceptions import ValidationError


def validate_year(value):
    today = dt.date.today()
    if value > today.year:
        raise ValidationError(
            'Год не может быть больше текущего.')
    return value


def validate_email(value):
    if len(value) > 254:
        raise ValidationError('Поле Email слишком длинное.')
    return value


def validate_username(value):
    if len(value) > 150:
        raise ValidationError('Поле username слишком длинное.')
    pattern = re.compile('^[a-zA-Z0-9_.+-@]+$')
    if value == 'me' or not pattern.match(value):
        raise ValidationError('Недопустимое имя пользователя.')
    return value


def validate_first_name(value):
    if len(value) > 150:
        raise ValidationError('first_name слишком длинное.')
    return value
