# publish-sink


```bash
bin/pulsar-admin sink create \
 --className PublishSink \
 --archive /opt/stream/publish-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name publish_sink \
 --inputs __acaction_publish \
 --sink-config-file /opt/stream/publish-sink-config.yml
```