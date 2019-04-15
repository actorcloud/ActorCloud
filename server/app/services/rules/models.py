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
    __tablename__ = 'business_rules'
    ruleName = db.Column(db.String(50))
    remark = db.Column(db.String(50))
    enable = db.Column(db.SmallInteger, default=1)
    sql = db.Column(db.String)
    fromTopics = db.Column(JSONB)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    tenantID = db.Column(db.String, db.ForeignKey('tenants.tenantID',
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))

    actions = db.relationship('Action',
                              secondary=BusinessRuleAction,
                              backref=db.backref('business_rules', lazy='dynamic'))


class Action(BaseModel):
    """
    config
    1 alert {"alertTitle": "","alertContent": "","alertSeverity":1}
    2 mail {"title": "","content": "",,"emails":["qwe@163.com","tyu@163.com"]}
    3 Webhook {"token": "jasdkjabsk","url": "http://127.0.0.1:6010"}
    """
    __tablename__ = 'actions'
    actionName = db.Column(db.String(50))
    actionType = db.Column(db.SmallInteger)  # 1：alert，2：mail，3：Webhook
    description = db.Column(db.String(300))
    config = db.Column(JSONB)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
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
