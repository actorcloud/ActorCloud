package client.demo;

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

public class RuleWindow {

  public static void main(String[] args) {

    Map<String, List<String>> messages = new HashMap<>();
    messages.put("room/temp", new ArrayList<>(Arrays.asList(
            "{\"temperature\":35,\"ts\":1541152485013}", //200
            "{\"temperature\":29,\"ts\":1541152485022}", //400
            "{\"temperature\":27,\"ts\":1541152485032}", //600
            "{\"temperature\":28,\"ts\":1541152485042}", //800
            "{\"temperature\":23,\"ts\":1541152485052}", //1000
            "{\"temperature\":25.2,\"ts\":1541152485062}", //1200
            "{\"temperature\":26.5,\"ts\":1541152485072}", //1400
            "{\"temperature\":27.1,\"ts\":1541152485082}", //1600
            "{\"temperature\":27.6,\"ts\":1541152485092}" //1800
    )));
    messages.put("room/light", new ArrayList<>(Arrays.asList(
            "{\"color\":\"red\",\"ts\":1541152485012}",
            "{\"color\":\"red\",\"ts\":1541152485022}",
            "{\"color\":\"red\",\"ts\":1541152485032}",
            "{\"color\":\"blue\",\"ts\":1541152485042}",
            "{\"color\":\"blue\",\"ts\":1541152485052}",
            "{\"color\":\"red\",\"ts\":1541152485062}",
            "{\"color\":\"blue\",\"ts\":1541152485072}",
            "{\"color\":\"blue\",\"ts\":1541152485082}",
            "{\"color\":\"red\",\"ts\":1541152485092}"
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
            Thread.sleep(200);
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