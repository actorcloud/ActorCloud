package io.emqx.stream.client.pulsar;

import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;

public class Sample {



  @SuppressWarnings("InfiniteLoopStatement")
  public static void main(String[] args) throws PulsarClientException {
    String namespace = "sample/standalone/ns1"; // This namespace is created automatically
    String topic = String.format("persistent://%s/my-topic", namespace);
    PulsarClient client = PulsarClient.builder()
            .serviceUrl("pulsar://127.0.0.1:6650")
            .build();
    Consumer<byte[]> consumer = client.newConsumer()
            .topic(topic)
            .subscriptionName("my-subscription")
            .subscribe();
    do {
      // Wait for a message
      Message<byte[]> msg = consumer.receive();

      System.out.printf("Message received: %s", new String(msg.getData()));

      // Acknowledge the message so that it can be deleted by the message broker
      consumer.acknowledge(msg);
    } while (true);

  }

}
