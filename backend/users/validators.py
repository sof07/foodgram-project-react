import re

from rest_framework.serializers import ValidationError


def validate_reserved_username(value):
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя "me" недоступно.')
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError('Недопустимое имя пользователя')
