# Device events aggregation
> 5th minute of every hour
* lwm2m protocol device events
* other protocol(mqtt, lora, Modbus) device events


### run
```bash
faust -A app.services.tasks_scheduler.device_events_aggr.app.faust_app worker -l info
```
