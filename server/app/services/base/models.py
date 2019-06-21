import bcrypt
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, db
from config import BaseConfig


__all__ = [
    'User', 'UserGroup', 'Role', 'Resource', 'Permission', 'Tenant',
    'DictCode', 'SystemInfo', 'Invitation', 'LoginLog',
    'Message', 'ActorTask', 'Service', 'UploadInfo'
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
    username = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    enable = db.Column(db.SmallInteger, server_default='1')
    _password = db.Column('password', db.String(100))
    lastRequestTime = db.Column(db.DateTime)
    loginTime = db.Column(db.DateTime)
    expiresAt = db.Column(db.DateTime)
    userAuthType = db.Column(db.Integer, server_default='1')  # 1: role 2: role+group
    groups = db.relationship('Group', secondary=UserGroup, lazy='dynamic')
    roleIntID = db.Column(db.Integer, db.ForeignKey('roles.id'))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID'))

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
    roleName = db.Column(db.String(50))
    description = db.Column(db.String(300))
    roleType = db.Column(db.SmallInteger)  # 1：user role 2：app role
    isShare = db.Column(db.SmallInteger, default=0)  # 0: private, 1: public
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         nullable=True)


class Resource(BaseModel):
    __tablename__ = 'resources'
    code = db.Column(db.String(50), unique=True)
    url = db.Column(db.String(50))
    method = db.Column(db.String(10))  # get post put delete
    order = db.Column(db.Integer)
    level = db.Column(db.Integer)
    icon = db.Column(db.String(50))
    enable = db.Column(db.SmallInteger, server_default='1')
    parentCode = db.Column(db.String(50), db.ForeignKey('resources.code'))
    tabs = db.Column(db.SmallInteger)
    children = db.relationship('Resource', cascade='all, delete-orphan')
    parent = db.relationship('Resource', remote_side=[code])
    service = db.Column(db.String(50))


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
    tenantType = db.Column(db.SmallInteger, default=1)  # 1: personal，2: company
    tenantID = db.Column(db.String(9), unique=True)
    company = db.Column(db.String(50), unique=True)
    companySize = db.Column(db.String(50))
    companyAddress = db.Column(db.String(50))
    contactPerson = db.Column(db.String(50))
    contactPhone = db.Column(db.String(50))
    contactEmail = db.Column(db.String(50))
    tenantBalance = db.Column(db.Float, server_default='0.00')
    invoiceBalance = db.Column(db.Float, server_default='0.00')
    enable = db.Column(db.SmallInteger, server_default='1')
    logo = db.Column(db.Integer,
                     db.ForeignKey('upload_info.id', onupdate="CASCADE"))
    logoDark = db.Column(db.Integer,
                         db.ForeignKey('upload_info.id', onupdate="CASCADE"))
    deviceCount = db.Column(db.Integer,
                            server_default=get_default_device_count())


class DictCode(BaseModel):
    __tablename__ = 'dict_code'
    code = db.Column(db.String(50))  # code的字段名
    codeValue = db.Column(db.SmallInteger)  # code的值
    codeStringValue = db.Column(db.String(50))  # code的字符串值
    enLabel = db.Column(db.String(50))  # en label
    zhLabel = db.Column(db.String(50))  # zh label


class SystemInfo(BaseModel):
    __tablename__ = 'system_info'
    key = db.Column(db.String(50))
    value = db.Column(db.String(50))


class Invitation(BaseModel):
    __tablename__ = 'invitations'
    inviteEmail = db.Column(db.String(50))
    roleIntID = db.Column(db.Integer)
    tenantID = db.Column(db.String(9))
    inviteStatus = db.Column(db.Integer, default=0)  # 0: not joined 1:joined
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))

    def generate_auth_token(self):
        expires_in = current_app.config['TOKEN_LIFETIME_INVITATION']
        s = JWT(current_app.config['SECRET_KEY'], expires_in=expires_in)
        token = s.dumps({
            'invitation_id': self.id
        })
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token


class LoginLog(BaseModel):
    __tablename__ = 'login_logs'
    IP = db.Column(db.String(50))  # IP
    isLogged = db.Column(db.SmallInteger)  # 0:failed，1:success
    loginTime = db.Column(db.DateTime)
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))


class Message(BaseModel):
    __tablename__ = 'messages'
    msgTitle = db.Column(db.String(100))
    msgContent = db.Column(db.String(300))
    messageType = db.Column(db.Integer)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         nullable=True)


class ActorTask(BaseModel):
    __tablename__ = 'actor_tasks'
    taskID = db.Column(db.String(50), unique=True)
    taskName = db.Column(db.String(512))
    taskStatus = db.Column(db.SmallInteger)  # 1:Waiting 2:Executing 3:Success 4:Failed 5:Retry
    taskCount = db.Column(db.SmallInteger, server_default='1')
    taskInfo = db.Column(JSONB)
    taskProgress = db.Column(db.Integer, server_default='0')
    taskResult = db.Column(JSONB)


class Service(BaseModel):
    __tablename__ = 'services'
    serviceName = db.Column(db.String(50))
    overview = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    chargeType = db.Column(db.SmallInteger)
    unitPrice = db.Column(db.Float, server_default='0.00')
    enable = db.Column(db.SmallInteger, default=0)
    serviceGroup = db.Column(db.SmallInteger)
    icon = db.Column(db.String(50))
    screenshots = db.Column(db.JSON)
    code = db.Column(db.String(50))
    referService = db.Column(db.String(50))
    order = db.Column(db.SmallInteger)


class UploadInfo(BaseModel):
    __tablename__ = 'upload_info'
    fileName = db.Column(db.String(300))
    displayName = db.Column(db.String(300))
    fileType = db.Column(db.SmallInteger, default=1)  # 1: package, 2:image
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
