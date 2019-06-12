# Pulsar Source Connector for EMQX

This is the source connector to subscribe to emqx and then feed into pulsar.

## How to Run

Assume emqtt and pulsar are run at localhost. 
0. Change the config for emqtt to not listen on localhost:8080, because 8080 is also used by pulsar
1. Run `mvn install -DskipTests`, make sure emqx-x.x.x-xxxxxx.nar is produced at /target
2. Open pulsar, run pulsar admin to add new source connector. Example:
`sudo ./pulsar-admin source localrun --className  EMQXSource -a ~/emqx-0.0.1-SNAPSHOT.nar --tenant public --namespace default --name emqx-source --destinationTopicName tttoxic`
3. Start a pulsar client to consume topic tttoxic or any topic specified at step 2
4. Open emqtt, try to publish message to topic /sample. Make sure pulsar client receives the topic.

# Pulsar Sink Connector for EMQX

## How to run

```bash
bin/pulsar-admin sink create \
 --className EMQXSink \
 --archive /opt/stream/emqx-source-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_mqtt \
 --inputs __acaction_mqtt \
 --sink-config '{"brokerUrl":"tcp://127.0.0.1:11883"}'
```