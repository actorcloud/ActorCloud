package io.emqx.stream.client.pulsar;

import org.apache.log4j.BasicConfigurator;
import org.apache.pulsar.client.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ProducerSample {
  private static final Logger log = LoggerFactory.getLogger(ProducerSample.class);

  public static void main(String[] args) throws IOException {
    BasicConfigurator.configure();
    String SERVICE_URL = args[0];
    String TOPIC_NAME = args[1];
    // Create a Pulsar client instance. A single instance can be shared across many
    // producers and consumer within the same application
    PulsarClient client = PulsarClient.builder()
            .serviceUrl(SERVICE_URL)
            .build();

    // Here you get the chance to configure producer specific settings
    Producer<byte[]> producer = client.newProducer()
            // Set the topic
            .topic(TOPIC_NAME)
            // Enable compression
            .compressionType(CompressionType.LZ4)
            .create();

    // Once the producer is created, it can be used for the entire application life-cycle
    log.info("Created producer for the topic {}", TOPIC_NAME);

    List<String> messages = new ArrayList<>(Arrays.asList(
            "{\"temperature\":35,\"ts\":1541152485013}", //200
            "{\"temperature\":29,\"ts\":1541152485022}", //400
            "{\"temperature\":27,\"ts\":1541152485032}", //600
            "{\"temperature\":28,\"ts\":1541152485042}", //800
            "{\"temperature\":23,\"ts\":1541152485052}", //1000
            "{\"temperature\":25.2,\"ts\":1541152485062}", //1200
            "{\"temperature\":26.5,\"ts\":1541152485072}", //1400
            "{\"temperature\":27.1,\"ts\":1541152485082}", //1600
            "{\"temperature\":27.6,\"ts\":1541152485092}" //1800
    ));

    // Send 10 test messages
    messages.forEach(message -> {

      // Send each message and log message content and ID when successfully received
      try {
        MessageId msgId = producer.send(message.getBytes());

        log.info("Published message '{}' with the ID {}", message, msgId);
      } catch (PulsarClientException e) {
        log.error(e.getMessage());
      }
    });

    client.close();
  }
}