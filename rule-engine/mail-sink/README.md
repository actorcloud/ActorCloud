# mail-sink


```bash
bin/pulsar-admin sink create \
 --className MailSink \
 --archive /opt/stream/mail-sink-x.y.z.nar \
 --tenant public \
 --namespace default \
 --name mail_sink \
 --inputs __acaction_mail \
 --sink-config-file /opt/stream/mail-sink-config.yml
```