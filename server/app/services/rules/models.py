from sqlalchemy.dialects.postgresql.json import JSONB

from actor_libs.database.orm import BaseModel, db


__all__ = [
    'RuleAction', 'Rule', 'Action'
]

RuleAction = db.Table(
    'rules_actions',
    db.Column('ruleIntID', db.Integer,
              db.ForeignKey('rules.id', onupdate="CASCADE", ondelete="CASCADE")),
    db.Column('actionIntID', db.Integer, db.ForeignKey('actions.id')),
)


class Rule(BaseModel):
    __tablename__ = 'rules'
    ruleName = db.Column(db.String(50))
    remark = db.Column(db.String(50))
    enable = db.Column(db.SmallInteger, default=1)
    sql = db.Column(db.String)
    fromTopics = db.Column(JSONB)
    ruleType = db.Column(db.SmallInteger)
    userIntID = db.Column(db.Integer, db.ForeignKey('users.id'))
    tenantID = db.Column(db.String, db.ForeignKey('tenants.tenantID',
                                                  onupdate="CASCADE",
                                                  ondelete="CASCADE"))

    actions = db.relationship('Action',
                              secondary=RuleAction,
                              backref=db.backref('rules', lazy='dynamic'))


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
