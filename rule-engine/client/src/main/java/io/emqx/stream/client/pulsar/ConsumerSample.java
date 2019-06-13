package io.emqx.stream.client.pulsar;

import java.io.IOException;

import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.SubscriptionType;

public class ConsumerSample {
  private static final String SUBSCRIPTION_NAME = "tutorial-subscription";

  public static void main(String[] args) throws IOException {
    String SERVICE_URL = args[0];
    String TOPIC_NAME = args[1];
    // Create a Pulsar client instance. A single instance can be shared across many
    // producers and consumer within the same application
    PulsarClient client = PulsarClient.builder()
            .serviceUrl(SERVICE_URL)
            .build();

    // Here you get the chance to configure consumer specific settings. eg:
    Consumer<byte[]> consumer = client.newConsumer()
            .topic(TOPIC_NAME)
            // Allow multiple consumers to attach to the same subscription
            // and get messages dispatched as a queue
            .subscriptionType(SubscriptionType.Shared)
            .subscriptionName(SUBSCRIPTION_NAME)
            .subscribe();


    // Once the consumer is created, it can be used for the entire application lifecycle
    System.out.println("Created consumer for the topic " + TOPIC_NAME);

    //noinspection InfiniteLoopStatement
    do {

      // Wait until a message is available
      Message<byte[]> msg = consumer.receive();
      System.out.println("receive sth.");
      // Extract the message as a printable string and then log
      String content = new String(msg.getData());
      System.out.println("Received message '" + content + "' with ID " + msg.getMessageId());

      // Acknowledge processing of the message so that it can be deleted
      consumer.acknowledge(msg);
    } while (true);
  }
}