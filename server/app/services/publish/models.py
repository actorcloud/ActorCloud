from sqlalchemy.dialects.postgresql import JSONB

from actor_libs.database.orm import BaseModel, db


__all__ = ['ClientPublishLog', 'TimerPublish']


class ClientPublishLog(BaseModel):
    __tablename__ = 'client_publish_logs'
    path = db.Column(db.String(500))  # lwm2m path
    topic = db.Column(db.String(500))  # mqtt topic
    taskID = db.Column(db.String(64), unique=True)  # 设备下发消息任务
    controlType = db.Column(db.SmallInteger, server_default='1')  # 1 消息下发，2 读 3 写 4 执行
    payload = db.Column(JSONB)  # 设备下发消息内容
    publishStatus = db.Column(db.SmallInteger)  # 0 失败 1 已下发 2 已到达
    userIntID = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        onupdate="CASCADE", ondelete="CASCADE"))  # 用户id
    clientIntID = db.Column(db.Integer,
                            db.ForeignKey('clients.id',
                                          onupdate="CASCADE", ondelete="CASCADE"))  # 设备id


class TimerPublish(BaseModel):
    __tablename__ = 'timer_publish'
    taskName = db.Column(db.String)  # 任务名
    taskStatus = db.Column(db.SmallInteger, server_default='2')  # 任务状态2 执行 3 成功
    timerType = db.Column(db.SmallInteger)  # 定时类型1 固定 , 2 间隔
    controlType = db.Column(db.SmallInteger)  # 下发类型
    topic = db.Column(db.String(500))  # 主题(mqtt)
    path = db.Column(db.String(500))  # lwm2m path
    payload = db.Column(JSONB)  # 下发消息内容
    intervalTime = db.Column(JSONB)  # 间隔时间{'weekday': 'hour': 'minute'}
    crontabTime = db.Column(db.DateTime)  # 指定下发时间
    clientIntID = db.Column(db.Integer, db.ForeignKey(
        'clients.id', onupdate="CASCADE", ondelete="CASCADE"))  # 设备id
    userIntID = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"))  # 用户
