# mail-sink


```bash
bin/pulsar-admin sink create \
 --className io.emqx.pulsar.io.MailSink \
 --archive /opt/stream/mail-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name __sink_mail \
 --inputs __acaction_mail \
 --sink-config-file /opt/stream/mail-sink-config.yml
```