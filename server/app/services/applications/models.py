from sqlalchemy import func

from actor_libs.database.orm import db, BaseModel
from actor_libs.utils import generate_uuid


__all__ = [
    'Application', 'ApplicationGroup', 'AppApiLog',
    'AppApiLogHour', 'AppApiLogDay', 'AppApiLogMonth'
]


def random_app_uid():
    """ Generate a 6-bit app identifier """

    app_uid = generate_uuid(size=6)
    application = db.session.query(func.count(Application.id)) \
        .filter(Application.appID == app_uid).scalar()
    if application:
        app_uid = random_app_uid()
    return app_uid


ApplicationGroup = db.Table(
    'applications_groups',
    db.Column('applicationIntID', db.Integer,
              db.ForeignKey('applications.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('groupID', db.String,
              db.ForeignKey('groups.groupID', onupdate="CASCADE", ondelete="CASCADE")),
)


class Application(BaseModel):
    __tablename__ = 'applications'
    appID = db.Column(db.String(6), default=random_app_uid, unique=True)
    appName = db.Column(db.String(50))
    appToken = db.Column(db.String(100), default=generate_uuid)  # 32-bit
    expiredAt = db.Column(db.DateTime)  # app token expired time
    description = db.Column(db.String(300))
    appStatus = db.Column(db.Integer)  # 0:blocked，1:run
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    roleIntID = db.Column(db.Integer, db.ForeignKey('roles.id'))  # app role id
    groups = db.relationship('Group', secondary=ApplicationGroup, lazy='dynamic')


class AppApiLog(BaseModel):
    __tablename__ = 'app_api_logs'
    createAt = db.Column(db.DateTime, server_default=func.now())
    url = db.Column(db.String(200))
    method = db.Column(db.String(100))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class AppApiLogHour(BaseModel):
    __tablename__ = 'app_api_logs_hour'
    countTime = db.Column(db.DateTime)
    apiCount = db.Column(db.Integer)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class AppApiLogDay(BaseModel):
    __tablename__ = 'app_api_logs_day'
    countTime = db.Column(db.DateTime)
    apiCount = db.Column(db.Integer)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class AppApiLogMonth(BaseModel):
    __tablename__ = 'app_api_logs_month'
    countTime = db.Column(db.DateTime)  # 统计时间
    apiCount = db.Column(db.Integer)  # 应用api调用月统计数量
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
