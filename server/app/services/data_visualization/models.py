from actor_libs.database.orm import ModelMixin, db


__all__ = [
    'DataPointEventHour', 'DataPointEventDay', 'DataPointEventMonth',
    'Lwm2mEventHour', 'Lwm2mEventDay', 'Lwm2mEventMonth'
]


class BaseAggr(ModelMixin, db.Model):
    __abstract__ = True
    minValue = db.Column(db.Float)
    maxValue = db.Column(db.Float)
    avgValue = db.Column(db.Float)
    sumValue = db.Column(db.Float)
    minCalc = db.Column(db.Float)
    maxCalc = db.Column(db.Float)
    avgCalc = db.Column(db.Float)
    sumCalc = db.Column(db.Float)


class DataPointEventHour(BaseAggr):
    __tablename__ = 'data_point_event_hour'
    __table_args__ = (
        db.Index('data_point_event_hour_countTime_idx', "countTime"),
    )
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"), primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    topic = db.Column(db.String(500), primary_key=True)
    dataPointID = db.Column(db.String(200), primary_key=True)


class DataPointEventDay(BaseAggr):
    __tablename__ = 'data_point_event_day'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    topic = db.Column(db.String(500), primary_key=True)
    dataPointID = db.Column(db.String(200), primary_key=True)


class DataPointEventMonth(BaseAggr):
    __tablename__ = 'data_point_event_month'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    topic = db.Column(db.String(500), primary_key=True)
    dataPointID = db.Column(db.String(200), primary_key=True)


class Lwm2mEventHour(BaseAggr):
    __tablename__ = 'lwm2m_event_hour'
    __table_args__ = (
        db.Index('lwm2m_event_hour_countTime_idx', "countTime"),
    )
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    path = db.Column(db.String(50), primary_key=True)  # /object_id/instance_id/item_id
    objectItem = db.Column(db.String(50))  # /object_id/item_id


class Lwm2mEventDay(BaseAggr):
    __tablename__ = 'lwm2m_event_day'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    path = db.Column(db.String(50), primary_key=True)  # /object_id/instance_id/item_id
    objectItem = db.Column(db.String(50))  # /object_id/item_id


class Lwm2mEventMonth(BaseAggr):
    __tablename__ = 'lwm2m_event_month'
    countTime = db.Column(db.DateTime, primary_key=True)
    tenantID = db.Column(db.String,
                         db.ForeignKey('tenants.tenantID',
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                         primary_key=True)
    productID = db.Column(db.String,
                          db.ForeignKey('products.productID',
                                        onupdate="CASCADE",
                                        ondelete="CASCADE"))
    deviceID = db.Column(db.String(100), primary_key=True)
    path = db.Column(db.String(50), primary_key=True)  # /object_id/instance_id/item_id
    objectItem = db.Column(db.String(50))  # /object_id/item_id
