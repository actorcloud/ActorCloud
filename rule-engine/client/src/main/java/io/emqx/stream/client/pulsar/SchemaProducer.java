package io.emqx.stream.client.pulsar;

import com.google.gson.Gson;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.impl.schema.AvroSchema;

import lombok.Data;

import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;


public class SchemaProducer {
  @Data
  public static class Foo {
    private Timestamp msgTime;
    private String tenantID;
    private String productID;
    private String deviceID;
    private String topic;
    private String payload_string;
    private String payload_json;
  }

  public static void main(String[] args) throws Exception {
    PulsarClient pulsarClient = PulsarClient.builder().serviceUrl("pulsar://192.168.0.2:6650").build();
    Producer<Foo> producer = pulsarClient.newProducer(AvroSchema.of(Foo.class)).topic("test_topic").create();

    for (int i = 10; i < 20; i++) {
      String payload = randomPayload();
      Foo foo = new Foo();
      foo.setMsgTime(new Timestamp(System.currentTimeMillis()));
      foo.setTenantID("myTenant" + (i%4));
      foo.setProductID("myProduct" + (i%6));
      foo.setDeviceID("myDevice" + (i%9));
      foo.setTopic("myTopic" + (i%3));
      foo.setPayload_json(payload);
      foo.setPayload_string(payload);
      producer.newMessage().value(foo).send();
    }
    System.out.println("sent");
    producer.close();
    pulsarClient.close();
  }

  private static String randomPayload() {
    double hum = 10.0 + Math.random() * 89.0;
    double temp = -25.0 + Math.random() * 65.0;
    Map<String, Double> payload = new HashMap<>();
    payload.put("hum", hum);
    payload.put("temp", temp);
    return new Gson().toJson(payload);
  }
}