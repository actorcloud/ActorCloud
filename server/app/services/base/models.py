import random
import string

import bcrypt
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.configs import BaseConfig
from actor_libs.database.orm import BaseModel, db


__all__ = [
    'User', 'Role', 'Resource', 'Permission', 'Tenant',
    'DictCode', 'SystemInfo', 'Invitation', 'LoginLog',
    'Message', 'UserGroup', 'ActorTask', 'Service'
]


def get_default_device_count():
    """ Get the number of devices that tenant can manage """

    base_config = BaseConfig()
    default_devices_limit = base_config.config['DEFAULT_DEVICES_LIMIT']
    return str(default_devices_limit)


UserGroup = db.Table(
    'users_groups',
    db.Column('userIntID', db.Integer,
              db.ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"),
              primary_key=True),
    db.Column('groupID', db.String(6),
              db.ForeignKey('groups.groupID', onupdate="CASCADE", ondelete="CASCADE"),
              primary_key=True),
)


class User(BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(50))  # 用户名
    nickname = db.Column(db.String(50))  # 昵称
    email = db.Column(db.String(50), unique=True)  # 邮箱
    department = db.Column(db.String(50))  # 部门
    phone = db.Column(db.String(50))  # 电话
    enable = db.Column(db.SmallInteger, server_default='1')  # 是否能登录
    _password = db.Column('password', db.String(100))  # 密码
    lastRequestTime = db.Column(db.DateTime)  # 最后访问时间
    loginTime = db.Column(db.DateTime)  # 登录时间
    expiresAt = db.Column(db.DateTime)  # 到期时间
    userAuthType = db.Column(db.Integer, server_default='1')  # 用户验证类型(1 基于角色 2 基于角色和分组)
    groups = db.relationship('Group', secondary=UserGroup, lazy='dynamic')  # user groups
    roleIntID = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 角色ID
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID'))  # 租户ID外键

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        bcrypt_rounds = current_app.config.get('BCRYPT_ROUNDS')
        bcrypt_prefix = current_app.config.get('BCRYPT_PREFIX').encode()
        raw_password = self._str_to_bytes(raw)
        bcrypt_password = bcrypt.hashpw(
            raw_password, bcrypt.gensalt(rounds=bcrypt_rounds, prefix=bcrypt_prefix)
        )
        self._password = self._byte_to_str(bcrypt_password)

    def check_password(self, raw):
        if not self._password:
            return False
        password = self._str_to_bytes(raw)
        hashed_password = self._str_to_bytes(self._password)
        return bcrypt.checkpw(password, hashed_password)

    def generate_auth_token(self, remember=False):
        if remember:
            expires_in = current_app.config['TOKEN_LIFETIME_REMEMBER']
        else:
            expires_in = current_app.config['TOKEN_LIFETIME']
        s = JWT(current_app.config['SECRET_KEY'], expires_in=expires_in)
        token = s.dumps({
            'user_id': self.id,
            'role_id': self.roleIntID,
            'tenant_uid': self.tenantID})
        return self._byte_to_str(token)

    @staticmethod
    def _str_to_bytes(raw_string):
        if isinstance(raw_string, str):
            bytes_object = raw_string.encode('utf-8')
        else:
            bytes_object = raw_string

        return bytes_object

    @staticmethod
    def _byte_to_str(row_byte):
        if isinstance(row_byte, bytes):
            row_str = row_byte.decode('utf-8')
        else:
            row_str = row_byte
        return row_str


class Role(BaseModel):
    __tablename__ = 'roles'
    roleName = db.Column(db.String(50))  # 角色名
    description = db.Column(db.String(300))  # 描述
    roleType = db.Column(db.SmallInteger)  # 角色类型，1：用户角色 2：应用角色
    isShare = db.Column(db.SmallInteger, default=0)  # 角色是否公用1公用， 0私有
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         nullable=True)


class Resource(BaseModel):
    __tablename__ = 'resources'
    code = db.Column(db.String(50), unique=True)  # 资源唯一标识, 前端根据code的内容来翻译
    url = db.Column(db.String(50))  # 资源url
    method = db.Column(db.String(10))  # 请求方法 get post put delete
    order = db.Column(db.Integer)  # 显示顺序，只对菜单类型有效
    level = db.Column(db.Integer)  # 资源级别：一级、二级、三级
    icon = db.Column(db.String(50))  # 一级菜单图标
    enable = db.Column(db.SmallInteger, server_default='1')  # 是否启用该资源
    parentCode = db.Column(db.String(50),
                           db.ForeignKey('resources.code'))  # 上级资源Code
    tabs = db.Column(db.SmallInteger)  # 是否包含tabs
    children = db.relationship('Resource', cascade='all, delete-orphan')  # 子资源
    parent = db.relationship('Resource', remote_side=[code])
    service = db.Column(db.String(50))  # resource 所属服务


class Permission(BaseModel):
    __tablename__ = 'permissions'
    roleIntID = db.Column(
        db.Integer,
        db.ForeignKey('roles.id', onupdate="CASCADE", ondelete="CASCADE")
    )
    resourceIntID = db.Column(
        db.Integer,
        db.ForeignKey('resources.id', onupdate="CASCADE", ondelete="CASCADE")
    )


class Tenant(BaseModel):
    __tablename__ = 'tenants'
    tenantType = db.Column(db.SmallInteger, default=1)  # 租户类型：1个人，2企业
    tenantID = db.Column(db.String(9), unique=True)  # 9位不重复租户ID，企业为C开头，个人为P开头
    company = db.Column(db.String(50), unique=True)  # 企业名称，个人用户为空
    companySize = db.Column(db.String(50))  # 企业规模
    companyAddress = db.Column(db.String(50))  # 企业地址
    contactPerson = db.Column(db.String(50))  # 联系人
    contactPhone = db.Column(db.String(50))  # 联系电话
    contactEmail = db.Column(db.String(50))  # 联系邮箱
    tenantBalance = db.Column(db.Float, server_default='0.00')  # 账户余额
    invoiceBalance = db.Column(db.Float, server_default='0.00')  # 开票余额
    enable = db.Column(db.SmallInteger, server_default='1')  # 是否可用
    logo = db.Column(db.Integer,
                     db.ForeignKey('upload_info.id', onupdate="CASCADE"))
    logoDark = db.Column(db.Integer,
                         db.ForeignKey('upload_info.id', onupdate="CASCADE"))
    deviceCount = db.Column(db.Integer,
                            server_default=get_default_device_count())  # 设备数量限制


class DictCode(BaseModel):
    __tablename__ = 'dict_code'
    code = db.Column(db.String(50))  # code的字段名
    codeValue = db.Column(db.SmallInteger)  # code的值
    codeStringValue = db.Column(db.String(50))  # code的字符串值
    enLabel = db.Column(db.String(50))  # en label
    zhLabel = db.Column(db.String(50))  # zh label


class SystemInfo(BaseModel):
    __tablename__ = 'system_info'
    key = db.Column(db.String(50))  # 存储的 key
    value = db.Column(db.String(50))  # key 对应的值


class Invitation(BaseModel):
    __tablename__ = 'invitations'
    inviteEmail = db.Column(db.String(50))  # 被邀请人邮箱
    roleIntID = db.Column(db.Integer)  # 角色id
    tenantID = db.Column(db.String(9))  # 租户id
    inviteStatus = db.Column(db.Integer, default=0)  # 邀请状态，0:未加入，1:已加入
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))

    def generate_auth_token(self):
        expires_in = current_app.config['TOKEN_LIFETIME_INVITATION']
        s = JWT(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({
            'invitation_id': self.id
        })


class LoginLog(BaseModel):
    __tablename__ = 'login_logs'
    IP = db.Column(db.String(50))  # IP
    isLogged = db.Column(db.SmallInteger)  # 登录结果 失败0，成功1
    loginTime = db.Column(db.DateTime)  # 登录时间
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))


class Message(BaseModel):
    __tablename__ = 'messages'
    msgTitle = db.Column(db.String(100))  # 消息标题
    msgContent = db.Column(db.String(300))  # 消息内容
    messageType = db.Column(db.Integer)  # 消息类型，1:财务消息，2:产品消息，3:安全消息，4:其它消息，5:公告
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         nullable=True)


class ActorTask(BaseModel):
    __tablename__ = 'actor_tasks'
    taskID = db.Column(db.String(50), unique=True)  # 任务ID
    taskName = db.Column(db.String(512))  # 任务名称
    taskStatus = db.Column(db.SmallInteger)  # 任务状态 1 等待 2 执行 3 成功 4 失败 5 重试
    taskCount = db.Column(db.SmallInteger, server_default='1')  # 任务执行次数
    taskInfo = db.Column(JSONB)  # 任务信息
    taskProgress = db.Column(db.Integer, server_default='0')  # 任务执行进度
    taskResult = db.Column(JSONB)  # 任务执行结果


class Service(BaseModel):
    __tablename__ = 'services'
    serviceName = db.Column(db.String(50))  # 服务名称
    overview = db.Column(db.String(50))  # 服务简介
    description = db.Column(db.String(1000))  # 具体介绍
    chargeType = db.Column(db.SmallInteger)  # 计费方式1：免费，2：时长（天），3：次数，4：条数（流量）
    unitPrice = db.Column(db.Float, server_default='0.00')  # 单价
    enable = db.Column(db.SmallInteger, default=0)  # 是否启动0 未启动, 1启动
    serviceGroup = db.Column(db.SmallInteger)  # 服务分组1 基础 2 DMP 3 AEP
    icon = db.Column(db.String(50))  # 图标
    screenshots = db.Column(db.JSON)  # 截图
    code = db.Column(db.String(50))  # 服务唯一标识
    referService = db.Column(db.String(50))  # 该服务引用的服务的code
    order = db.Column(db.SmallInteger)  # 顺序
