from marshmallow import Schema, fields


class BasePaginationInputSchema(Schema):
    '''Base schema of pagination input.'''
    per_page = fields.Int(missing=25)
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
    pass
