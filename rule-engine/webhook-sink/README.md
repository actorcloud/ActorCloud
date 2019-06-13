# webhook-sink


```bash
bin/pulsar-admin sink create \
 --className io.emqx.pulsar.io.WebhookSink \
 --archive /opt/stream/webhook-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_webhook \
 --inputs __acaction_webhook \
```