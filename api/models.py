from tortoise.models import Model
from tortoise import fields


class UserModel(Model):
    id = fields.CharField(max_length=255, pk=True)
    roles: fields.ManyToManyRelation['RoleModel'] = fields.ManyToManyField(
        'models.RoleModel',
        related_name='roles',
        through='user_role',
    )

    def __str__(self):
        return self.name


class RoleModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(default='')
    permissions = fields.JSONField(
        default={
            'databases': [],
            'action_ids': [],
        }
    )

    users: fields.ManyToManyRelation
