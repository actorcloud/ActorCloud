from sqlalchemy import func

from actor_libs.database.orm import db, BaseModel
from actor_libs.utils import generate_uuid


__all__ = [
    'Application', 'ApplicationProduct', 'AppApiLog',
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


ApplicationProduct = db.Table(
    'app_product',
    db.Column('applicationIntID', db.Integer,
              db.ForeignKey('applications.id',
                            onupdate="CASCADE",
                            ondelete="CASCADE")),
    db.Column('productIntID', db.Integer, db.ForeignKey('products.id')),
)


class Application(BaseModel):
    __tablename__ = 'applications'
    appID = db.Column(db.String(6),
                      default=random_app_uid, unique=True)  # 应用ID
    appName = db.Column(db.String(50))  # 应用名称
    appToken = db.Column(db.String(100), default=generate_uuid)  # 应用密钥
    expiredAt = db.Column(db.DateTime)  # 应用到期日期
    description = db.Column(db.String(300))  # 应用描述
    appStatus = db.Column(db.Integer)  # 应用状态，0:不可用，1:可用
    userIntID = db.Column(db.ForeignKey('users.id'))  # 用户ID
    roleIntID = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 角色ID
    products = db.relationship('Product',
                               secondary=ApplicationProduct,
                               backref=db.backref('applications',
                                                  lazy='joined'),
                               lazy='dynamic')


class AppApiLog(BaseModel):
    __tablename__ = 'app_api_logs'
    createAt = db.Column(db.DateTime, server_default=func.now())
    url = db.Column(db.String(200))  # 接口地址
    method = db.Column(db.String(100))  # 请求方法
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class AppApiLogHour(BaseModel):
    __tablename__ = 'app_api_logs_hour'
    countTime = db.Column(db.DateTime)  # 统计时间
    apiCount = db.Column(db.Integer)  # 应用api调用小时统计数量
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class AppApiLogDay(BaseModel):
    __tablename__ = 'app_api_logs_day'
    countTime = db.Column(db.DateTime)  # 统计时间
    apiCount = db.Column(db.Integer)  # 应用api调用天统计数量
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
