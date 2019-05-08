from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import ModelMixin, db


__all__ = [
    'DeviceEvent', 'DeviceEventsHour', 'DeviceEventsDay', 'DeviceEventsMonth',
    'ConnectLog'
]


class DeviceEvent(ModelMixin, db.Model):
    """ device upload event """
    __tablename__ = 'device_events'
    __table_args__ = (
        db.Index('device_events_msgTime_idx', "msgTime"),
    )
    msgTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String(9), primary_key=True)
    deviceID = db.Column(db.String(100), primary_key=True)
    dataType = db.Column(db.SmallInteger, primary_key=True)  # 1:event  2:response
    topic = db.Column(db.String(500))
    streamID = db.Column(db.String(100))
    data = db.Column(JSONB)
    responseResult = db.Column(JSONB)


class BaseAggr(ModelMixin, db.Model):
    __abstract__ = True
    minValue = db.Column(db.Float)
    maxValue = db.Column(db.Float)
    avgValue = db.Column(db.Float)
    sumValue = db.Column(db.Float)


class DeviceEventsHour(BaseAggr):
    __tablename__ = 'device_events_hour'
    __table_args__ = (
        db.Index('device_events_hour_countTime_idx', "countTime"),
    )
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"), primary_key=True)
    deviceID = db.Column(db.String(100), primary_key=True)
    streamID = db.Column(db.String(100), primary_key=True)
    dataPointID = db.Column(db.String(100), primary_key=True)


class DeviceEventsDay(BaseAggr):
    __tablename__ = 'device_events_day'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    deviceID = db.Column(db.String(100), primary_key=True)
    streamID = db.Column(db.String(100), primary_key=True)
    dataPointID = db.Column(db.String(100), primary_key=True)


class DeviceEventsMonth(BaseAggr):
    __tablename__ = 'device_events_month'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    deviceID = db.Column(db.String(100), primary_key=True)
    streamID = db.Column(db.String(100), primary_key=True)
    dataPointID = db.Column(db.String(200), primary_key=True)


class ConnectLog(ModelMixin, db.Model):
    """ client connect log """
    __tablename__ = 'connect_logs'
    __table_args__ = (
        db.Index('connect_logs_msgTime_idx', "msgTime"),
    )
    keepAlive = db.Column(db.Integer)
    IP = db.Column(db.String)
    connectStatus = db.Column(db.SmallInteger)  # 0:Offline, 1:Online, 2:AuthenticateFailed
    msgTime = db.Column(db.DateTime, server_default=func.now(), primary_key=True)
    deviceID = db.Column(db.String, primary_key=True)  # device uid
    tenantID = db.Column(db.String, primary_key=True)  # tenant uid
