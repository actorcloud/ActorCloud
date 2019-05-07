from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, db, ModelMixin


__all__ = ['PublishLog', 'TimerPublish']


class PublishLog(ModelMixin, db.Model):
    """
    controlType: 1:Publish,2:Read,3:Write,4 Execute
    publishStatus: 0:Failed,1:Published 2:Arrived
    """
    __tablename__ = 'publish_logs'
    __table_args__ = (
        db.Index('publish_logs_msgTime_idx', "msgTime"),
    )
    msgTime = db.Column(db.DateTime, server_default=func.now())  # publish time
    topic = db.Column(db.String(1000))  # mqtt topic
    streamID = db.Column(db.String(1000))  # stream id
    payload = db.Column(JSONB)  # publish payload
    publishStatus = db.Column(db.SmallInteger)
    taskID = db.Column(db.String(64), primary_key=True)
    tenantID = db.Column(db.String(9), primary_key=True)
    deviceID = db.Column(db.String(64), primary_key=True)


class TimerPublish(BaseModel):
    __tablename__ = 'timer_publish'
    taskName = db.Column(db.String)  # 任务名
    taskStatus = db.Column(db.SmallInteger, server_default='2')  # 任务状态2 执行 3 成功
    timerType = db.Column(db.SmallInteger)  # 定时类型1 固定 , 2 间隔
    topic = db.Column(db.String(1000))  # 主题(mqtt)
    payload = db.Column(JSONB)  # 下发消息内容
    intervalTime = db.Column(JSONB)  # 间隔时间{'weekday': 'hour': 'minute'}
    crontabTime = db.Column(db.DateTime)  # 指定下发时间
    deviceIntID = db.Column(db.Integer, db.ForeignKey(
        'devices.id', onupdate="CASCADE", ondelete="CASCADE"))  # 设备id
    userIntID = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"))  # 用户
