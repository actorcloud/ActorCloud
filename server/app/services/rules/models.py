from sqlalchemy.dialects.postgresql.json import JSONB

from actor_libs.database.orm import BaseModel, db


__all__ = [
    'BusinessRuleAction', 'BusinessRule', 'Action', 'MessageRule'
]


BusinessRuleAction = db.Table(
    'business_rules_actions',
    db.Column('businessRuleIntID', db.Integer,
              db.ForeignKey('business_rules.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('actionIntID', db.Integer, db.ForeignKey('actions.id')),
)


class BusinessRule(BaseModel):
    """
    frequency 频率  {"type":1,"times":3,"period":"12m/h"}
    conditions 条件 [{"data_point": "status", "operator": ">", "threshold": 3,
    "compare_data_point":"status2","relation":"and"}]
    """
    __tablename__ = 'business_rules'
    ruleName = db.Column(db.String(50))  # 规则名称
    remark = db.Column(db.String(50))  # 备注
    enable = db.Column(db.SmallInteger, default=1)  # 是否可用
    frequency = db.Column(JSONB)  # 频率
    conditions = db.Column(JSONB)  # 条件
    conditionType = db.Column(db.SmallInteger)  # 条件类型 1功能点 2指标公式 3未上报数据
    deviceID = db.Column(db.String(100))
    dataStreamIntID = db.Column(db.Integer,
                                db.ForeignKey('data_streams.id',
                                              onupdate="CASCADE",
                                              ondelete="CASCADE"))  # 关联数据流 id
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))  # 用户 id
    tenantID = db.Column(db.String, db.ForeignKey('tenants.tenantID',
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    groupID = db.Column(db.String,
                        db.ForeignKey('groups.groupID',
                                      onupdate="CASCADE",
                                      ondelete="CASCADE"))
    actions = db.relationship('Action',
                              secondary=BusinessRuleAction,
                              backref=db.backref('business_rules', lazy='dynamic'))


class Action(BaseModel):
    """
    config
    1 告警 {"content": "设备温度高于20度","title": "温度过高","alertSeverity":1}
    2 邮件 {"content": "设备温度高于20度","title": "温度过高","emails":["qwe@163.com","tyu@163.com"]}
    3 Webhook {"token": "jasdkjabsk","url": "http://127.0.0.1:6010"}
    """
    __tablename__ = 'actions'
    actionName = db.Column(db.String(50))  # 操作名称
    actionType = db.Column(db.SmallInteger)  # 操作类型：1：告警，2：邮件，3：Webhook
    description = db.Column(db.String(300))  # 描述
    config = db.Column(JSONB)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))  # 用户 id
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))


class MessageRule(BaseModel):
    __tablename__ = 'message_rules'
    ruleType = db.Column(db.SmallInteger)  # 规则类型，包含:1:webhook，2:backend，3:bridge
    remark = db.Column(db.String(50))  # 备注
    enable = db.Column(db.SmallInteger, default=1)  # 是否可用
    config = db.Column(JSONB)
    status = db.Column(db.SmallInteger)  # 规则状态 0：验证失败 1：验证成功
    productID = db.Column(db.String(100),
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    groupID = db.Column(db.String(100),
                        db.ForeignKey('groups.groupID',
                                      onupdate="CASCADE",
                                      ondelete="CASCADE"))
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"))
