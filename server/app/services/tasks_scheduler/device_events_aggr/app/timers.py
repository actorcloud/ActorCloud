from . import faust_app, project_config
from .tasks import device_events_aggr


@faust_app.crontab(cron_format='5 * * * *', timezone=project_config['TIMEZONE'])
async def device_events_aggr():
    """ Aggregate device events at 5th minute of every hour """

    await device_events_aggr.delay()
