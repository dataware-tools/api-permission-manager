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


class PermissionSchema(Schema):
    databases = fields.List(fields.Str())
    actions = fields.List(
        fields.Nested(ActionSchema)
    )


class RoleContentSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()
    permissions = fields.List(
        fields.Nested(PermissionSchema),
        required=True,
    )


class RoleSchema(RoleContentSchema):
    role_id = fields.Int(attribute='id')


class RolesResourceOnGetInputSchema(BasePaginationInputSchema):
    pass


class UserSchema(Schema):
    user_id = fields.Str()
    name = fields.Str()
    roles = fields.List(
        fields.Nested(RoleSchema, only=['role_id', 'name', 'description']),
        default=[],
    )


class UsersResourceInputSchema(BasePaginationInputSchema):
    # Auth0 has limitation on per_page up to 100
    per_page = fields.Int(
        missing=settings.PAGINATION['DEFAULT_PER_PAGE'],
        validate=validate.Range(min=1, max=100),
    )


class UserResourceOnPatchInputSchema(Schema):
    role_ids = fields.List(fields.Int())
