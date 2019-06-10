# actorcloud-db-sink


```bash
bin/pulsar-admin sink create \
 --className ActorcloudSink \
 --archive /opt/stream/actorcloud-db-sink-0.5.3.nar \
 --tenant public \
 --namespace default \
 --name ac_db_sink \
 --inputs __emqx_all \
 --sink-config-file /opt/stream/actorcloud-db-sink-config.yml
```