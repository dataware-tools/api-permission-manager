from marshmallow import Schema, fields, validate

from api import settings


class BasePaginationInputSchema(Schema):
    '''Base schema of pagination input.'''
    per_page = fields.Int(missing=settings.PAGINATION['DEFAULT_PER_PAGE'])
    page = fields.Int(missing=0)
    search = fields.Str(missing='')


class ActionSchema(Schema):
    action_id = fields.Str()
    name = fields.Str()


class RoleSchema(Schema):
    role_id = fields.Str(attribute='id')
    name = fields.Str()
    description = fields.Str()


class UserSchema(Schema):
    user_id = fields.Str()
    name = fields.Str()
    roles = fields.List(fields.Nested(RoleSchema))


class UsersResourceInputSchema(BasePaginationInputSchema):
    # Auth0 has limitation on per_page up to 100
    per_page = fields.Int(
        missing=settings.PAGINATION['DEFAULT_PER_PAGE'],
        validate=validate.Range(min=1, max=100),
    )
