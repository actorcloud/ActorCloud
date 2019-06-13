package io.emqx.stream.client.demo;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

public class RuleCommon {

  public static void main(String[] args) {

    Map<String, List<String>> messages = new HashMap<>();
    messages.put("sample/abc", new ArrayList<>(Arrays.asList(
            "{\"color\":\"red\",\"temperature\":25.2}",
            "{\"color\":\"red\",\"temperature\":26.1}",
            "{\"color\":\"red\",\"temperature\":27.3}",
            "{\"color\":\"red\",\"temperature\":26.5}",
            "{\"color\":\"red\",\"temperature\":25.3}",
            "{\"color\":\"red\",\"temperature\":24.4}",
            "{\"color\":\"red\",\"temperature\":23.7}",
            "{\"color\":\"red\",\"temperature\":25.6}",
            "{\"color\":\"red\",\"temperature\":26.2}"
    )));
    int qos = 2;
    String broker = "tcp://localhost:1883";
    String clientId = "JavaSample";
    MemoryPersistence persistence = new MemoryPersistence();

    try {
      MqttClient sampleClient = new MqttClient(broker, clientId, persistence);
      MqttConnectOptions connOpts = new MqttConnectOptions();
      connOpts.setCleanSession(true);
      System.out.println("Connecting to broker: " + broker);
      sampleClient.connect(connOpts);
      System.out.println("Connected");
      ExecutorService es = Executors.newCachedThreadPool();
      messages.forEach((topic, list) -> es.execute(() -> list.forEach(content -> {
          System.out.println("Publishing message: " + content + " to topic " + topic);
          MqttMessage message = new MqttMessage(content.getBytes());
          message.setQos(qos);
          try {
            sampleClient.publish(topic, message);
            Thread.sleep(500);
          } catch (InterruptedException | MqttException e) {
            e.printStackTrace();
          }
          System.out.println("Message published");
        })));
      es.shutdown();
      if(es.awaitTermination(2, TimeUnit.MINUTES)) {
        sampleClient.disconnect();
        System.out.println("Disconnected");
        System.exit(0);
      }
    } catch (MqttException me) {
      System.out.println("reason " + me.getReasonCode());
      System.out.println("msg " + me.getMessage());
      System.out.println("loc " + me.getLocalizedMessage());
      System.out.println("cause " + me.getCause());
      System.out.println("excep " + me);
      me.printStackTrace();
    } catch (InterruptedException e) {

      e.printStackTrace();
    }
  }
}
