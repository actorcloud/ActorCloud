# publish-sink


```bash
bin/pulsar-admin sink create \
 --className PublishSink \
 --archive /opt/stream/publish-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_publish \
 --inputs __acaction_publish \
 --sink-config-file /opt/stream/publish-sink-config.yml
```