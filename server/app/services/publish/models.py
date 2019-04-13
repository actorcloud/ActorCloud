from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, db


__all__ = ['DevicePublishLog', 'GroupPublishLog', 'TimerPublish']


class DevicePublishLog(BaseModel):
    __tablename__ = 'device_publish_logs'
    path = db.Column(db.String(500))  # lwm2m path
    topic = db.Column(db.String(500))  # mqtt topic
    taskID = db.Column(db.String(64), unique=True)  # 设备下发消息任务
    controlType = db.Column(db.SmallInteger, server_default='1')  # 1 消息下发，2 读 3 写 4 执行
    payload = db.Column(JSONB)  # 设备下发消息内容
    publishStatus = db.Column(db.SmallInteger)  # 0 失败 1 已下发 2 已到达
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE", ondelete="CASCADE"))  # 用户id
    deviceIntID = db.Column(db.Integer,
                            db.ForeignKey('clients.id',
                                          onupdate="CASCADE", ondelete="CASCADE"))  # 设备id
    groupControlLogIntID = db.Column(db.Integer,
                                     db.ForeignKey('group_publish_logs.id',
                                                   onupdate="CASCADE", ondelete="CASCADE"))


class GroupPublishLog(BaseModel):
    __tablename__ = 'group_publish_logs'
    path = db.Column(db.String(500))  # lwm2m path
    topic = db.Column(db.String(500))  # mqtt topic
    taskID = db.Column(db.String(64), unique=True)  # 设备下发消息任务ID
    controlType = db.Column(db.SmallInteger, server_default='1')  # 控制类型
    payload = db.Column(JSONB)  # payload
    publishStatus = db.Column(db.SmallInteger, default=0)  # 0 失败 1 已下发 2 已到达
    groupID = db.Column(db.String, db.ForeignKey(
        'groups.groupID', onupdate="CASCADE", ondelete="CASCADE"))  # 分组uid
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE", ondelete="CASCADE"))  # 用户id


class TimerPublish(BaseModel):
    __tablename__ = 'timer_publish'
    taskName = db.Column(db.String)  # 任务名
    taskStatus = db.Column(db.SmallInteger, server_default='2')  # 任务状态2 执行 3 成功
    timerType = db.Column(db.SmallInteger)  # 定时类型1 固定 , 2 间隔
    publishType = db.Column(db.SmallInteger)  # 0 设备下发, 1 分组下发
    controlType = db.Column(db.SmallInteger)  # 下发类型
    topic = db.Column(db.String(500))  # 主题(mqtt)
    path = db.Column(db.String(500))  # lwm2m path
    payload = db.Column(JSONB)  # 下发消息内容
    intervalTime = db.Column(JSONB)  # 间隔时间{'weekday': 'hour': 'minute'}
    crontabTime = db.Column(db.DateTime)  # 指定下发时间
    groupID = db.Column(db.String, db.ForeignKey(
        'groups.groupID', onupdate="CASCADE", ondelete="CASCADE"))  #分组 uid
    deviceIntID = db.Column(db.Integer, db.ForeignKey(
        'clients.id', onupdate="CASCADE", ondelete="CASCADE"))  # 设备id
    userIntID = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"))  # 用户
