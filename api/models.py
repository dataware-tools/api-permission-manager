from tortoise.models import Model
from tortoise import fields


class UserModel(Model):
    id = fields.CharField(max_length=255, pk=True)
    name = fields.CharField(max_length=255)
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

    users: fields.ManyToManyRelation
    permissions: fields.ReverseRelation['PermissionModel']


class PermissionModel(Model):
    id = fields.IntField(pk=True)
    role: fields.ForeignKeyRelation[RoleModel] = fields.ForeignKeyField(
        'models.RoleModel',
        related_name='permissions',
    )
    databases = fields.JSONField()
    actions = fields.JSONField()
