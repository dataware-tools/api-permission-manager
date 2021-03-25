from marshmallow import Schema, fields


class ActionSchema(Schema):
    action_id = fields.Str()
    name = fields.Str()
