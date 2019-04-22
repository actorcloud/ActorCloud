from flask import g
from marshmallow import post_load
from marshmallow.validate import OneOf

from actor_libs.errors import DataNotFound
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDateTime, EmqInteger, EmqList, EmqString
)
from app.models import Group


__all__ = ['ApplicationSchema']


class ApplicationSchema(BaseSchema):
    """ application management """

    appID = EmqString(dump_only=True)
    appName = EmqString(required=True)
    appToken = EmqString(dump_only=True)
    expiredAt = EmqDateTime(allow_none=True)  # expired time
    description = EmqString(allow_none=True, len_max=300)
    appStatus = EmqInteger(required=True, validate=OneOf([0, 1]))
    userIntID = EmqInteger(allow_none=True)
    roleIntID = EmqInteger(required=True)  # app role id
    groups = EmqList(allow_none=True, list_type=str, load_only=True)  # product uid

    @post_load
    def handle_app_groups(self, in_data):
        groups_uid = in_data.get('groups')
        if not groups_uid:
            return in_data
        groups = Group.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Group.groupID.in_(set(groups_uid))).all()
        if len(groups_uid) != len(groups):
            raise DataNotFound(field='groups')
        in_data['groups'] = groups
        return in_data
