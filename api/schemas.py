from marshmallow import Schema, fields, validate, post_dump

from api import settings


class BasePaginationInputSchema(Schema):
    '''Base schema of pagination input.'''
    per_page = fields.Int(missing=settings.PAGINATION['DEFAULT_PER_PAGE'])
    page = fields.Int(missing=0)
    search = fields.Str(missing='')


class ActionSchema(Schema):
    action_id = fields.Str()
    name = fields.Str()


class PermissionBaseSchema(Schema):
    databases = fields.List(fields.Str())
    actions = fields.List(fields.Str())


class PermissionDetailSchema(PermissionBaseSchema):
    @post_dump(pass_many=True)
    def fix_action_shape(self, data, many):
        '''Fix action shape to the detailed one.'''
        data['actions'] = [settings.ActionType[action].describe() for action in data['actions']]
        return data


class RoleBaseSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()
    permissions = fields.List(
        fields.Nested(PermissionBaseSchema),
        required=True,
    )


class RoleDetailSchema(RoleBaseSchema):
    role_id = fields.Int(attribute='id')
    permissions = fields.List(
        fields.Nested(PermissionDetailSchema),
    )


class RolesResourceOnGetInputSchema(BasePaginationInputSchema):
    pass


class UserSchema(Schema):
    user_id = fields.Str()
    name = fields.Str()
    roles = fields.List(
        fields.Nested(RoleDetailSchema, only=['role_id', 'name', 'description']),
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
