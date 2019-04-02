from actor_libs.schemas.base import BaseSchema


class CurrentAlertSchema(BaseSchema):
    class Meta:
        additional = (
            'deviceID', 'alertName', 'alertContent', 'alertTimes',
            'alertDetail', 'alertSeverity', 'startTime', 'ruleIntID',
            'scopeIntID'
        )


class HistoryAlertSchema(BaseSchema):
    class Meta:
        additional = (
            'deviceID', 'alertName', 'alertContent', 'alertTimes',
            'alertDetail', 'alertSeverity', 'startTime', 'endTime'
        )
