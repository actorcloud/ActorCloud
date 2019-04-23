from flask import g
from marshmallow import post_load, validates
from marshmallow.validate import OneOf

from actor_libs.errors import DataNotFound, DataExisted
from actor_libs.schemas import BaseSchema
from actor_libs.schemas.fields import (
    EmqDateTime, EmqInteger, EmqList, EmqString
)
from app.models import Group, Application


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

    @validates('appName')
    def validate_app_name(self, value):
        if self._validate_obj('appName', value):
            return
        app = Application.query \
            .filter_tenant(tenant_uid=g.tenant_uid) \
            .filter(Application.appName == value).first()
        if app:
            raise DataExisted(field='appName')

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
