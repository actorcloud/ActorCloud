from sqlalchemy import JSON, func

from actor_libs.database.orm import BaseModel, db


__all__ = ['CurrentAlert', 'HistoryAlert']


class CurrentAlert(BaseModel):
    __tablename__ = 'current_alerts'
    createAt = db.Column(db.DateTime, server_default=func.now())
    alertName = db.Column(db.String(50))
    alertContent = db.Column(db.String(300))
    alertTimes = db.Column(db.Integer)
    alertDetail = db.Column(JSON)
    alertSeverity = db.Column(db.SmallInteger)
    startTime = db.Column(db.DateTime)
    deviceID = db.Column(db.String(100))
    ruleIntID = db.Column(db.Integer,
                          db.ForeignKey('business_rules.id',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
    __table_args__ = (
        db.Index('alerts_rule_key',
                 'tenantID', 'deviceID', 'ruleIntID',
                 unique=True),
    )


class HistoryAlert(BaseModel):
    __tablename__ = 'history_alerts'
    createAt = db.Column(db.DateTime, server_default=func.now())
    alertName = db.Column(db.String(50))
    alertContent = db.Column(db.String(300))
    alertTimes = db.Column(db.Integer)
    alertDetail = db.Column(JSON)
    alertSeverity = db.Column(db.SmallInteger)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    deviceID = db.Column(db.String(100))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
