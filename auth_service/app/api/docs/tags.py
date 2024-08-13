from enum import Enum


class ApiTags(Enum):
    V1_AUTH = 'API V1 / Auth'
    V1_ROLES = 'API V1 / Roles'
    V1_USERS = 'API V1 / Users'


# Теги отображаются в Swagger в порядке, заданном в списке
api_tags = [
    {
        'name': ApiTags.V1_AUTH,
    },
    {
        'name': ApiTags.V1_ROLES,
    },
    {
        'name': ApiTags.V1_USERS,
    },
]
