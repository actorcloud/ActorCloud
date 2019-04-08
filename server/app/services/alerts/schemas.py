from actor_libs.schemas import BaseSchema


__all__ = ['CurrentAlertSchema', 'HistoryAlertSchema']


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
