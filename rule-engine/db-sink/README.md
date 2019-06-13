# db-sink

Run
```bash
bin/pulsar-admin sink create \
 --className io.emqx.pulsar.io.DatabaseSink \
 --archive /opt/stream/db-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_db \
 --inputs __acaction_db \
 --sink-config-file /opt/stream/db-sink-config.yml
```