# actorcloud-db-sink


```bash
bin/pulsar-admin sink create \
 --className io.emqx.pulsar.io.ActorcloudSink \
 --archive /opt/stream/actorcloud-db-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_ac_db \
 --inputs __emqx_all \
 --sink-config-file /opt/stream/actorcloud-db-sink-config.yml
```