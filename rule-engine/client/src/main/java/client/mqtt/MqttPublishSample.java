package client.mqtt;

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

/**
 * Firstly, start consumer to consumer __action_db2
 *  Rules to test
 *
 * {"id":"rulePlus","sql":"SELECT temperature,'plus' FROM \"/jsonup/CYzWtxrql/product1/+/topic4\" where temperature > 26.5","enabled":true, "actions":[{"db2":{"columns":{"msgTime":"ts","topic":"topic","payload":"payload","deviceID":"device_id","tenantID":"tenant_id"}}}]}
 * {"id":"ruleSharp","sql":"SELECT temperature,'sharp' FROM \"/jsonup/CYzWtxrql/product1/#\" where temperature > 26.5","enabled":true, "actions":[{"db2":{"columns":{"msgTime":"ts","topic":"topic","payload":"payload","deviceID":"device_id","tenantID":"tenant_id"}}}]}
 * {"id":"ruleSingle","sql":"SELECT temperature,'single' FROM \"/jsonup/CYzWtxrql/product1/device2/topic2\" where temperature > 26.5","enabled":true, "actions":[{"db2":{"columns":{"msgTime":"ts","topic":"topic","payload":"payload","deviceID":"device_id","tenantID":"tenant_id"}}}]}
 *{"id":"ruleTumble","sql":"SELECT *,'tumble' FROM \"/jsonup/CYzWtxrql/product2/device2/topic1\" where temperature > 26.5 group by tumblingwindow('tt', 3)","enabled":true,"actions":[{"db2":{"columns":{"msgTime":"ts","topic":"topic","payload":"payload","deviceID":"device_id","tenantID":"tenant_id"}}}]}
 *{"id":"ruleSlide","sql":"SELECT *,'slide' FROM \"/jsonup/CYzWtxrql/product2/device2/topic1\" where temperature > 26.5 group by slidingwindow('ss', 5) having count(*)>3","enabled":true,"actions":[{"db2":{"columns":{"msgTime":"ts","topic":"topic","payload":"payload","deviceID":"device_id","tenantID":"tenant_id"}}}]}
 */

public class MqttPublishSample {

  public static void main(String[] args) {

    Map<String, List<String>> messages = new HashMap<>();
    messages.put("/jsonup/CYzWtxrql/product1/device1/topic4", new ArrayList<>(Arrays.asList(
            "{\"temperature\":35,\"timestamp\":1541152485013}", //200
            "{\"temperature\":29,\"timestamp\":1541152485022}", //400
            "{\"temperature\":27,\"timestamp\":1541152485032}", //600
            "{\"temperature\":28,\"timestamp\":1541152485042}", //800
            "{\"temperature\":23,\"timestamp\":1541152485052}", //1000
            "{\"temperature\":25.2,\"timestamp\":1541152485062}", //1200
            "{\"temperature\":26.5,\"timestamp\":1541152485072}", //1400
            "{\"temperature\":27.1,\"timestamp\":1541152485082}", //1600
            "{\"temperature\":27.6,\"timestamp\":1541152485092}" //1800
    )));
    messages.put("/jsonup/CYzWtxrql/product2/device2/topic1", new ArrayList<>(Arrays.asList(
            "{\"temperature\":35,\"timestamp\":1541152486013}", //200
            "{\"temperature\":29,\"timestamp\":1541152486022}", //400
            "{\"temperature\":27,\"timestamp\":1541152486032}", //600
            "{\"temperature\":28,\"timestamp\":1541152486042}", //800
            "{\"temperature\":23,\"timestamp\":1541152486052}", //1000
            "{\"temperature\":25.2,\"timestamp\":1541152486062}", //1200
            "{\"temperature\":26.5,\"timestamp\":1541152486072}", //1400
            "{\"temperature\":27.1,\"timestamp\":1541152486082}", //1600
            "{\"temperature\":27.6,\"timestamp\":1541152486092}" //1800
    )));
    messages.put("/jsonup/CYzWtxrql/product1/device2/topic2", new ArrayList<>(Arrays.asList(
            "{\"temperature\":35,\"timestamp\":1541152487013}", //200
            "{\"temperature\":29,\"timestamp\":1541152487022}", //400
            "{\"temperature\":27,\"timestamp\":1541152487032}", //600
            "{\"temperature\":28,\"timestamp\":1541152487042}", //800
            "{\"temperature\":23,\"timestamp\":1541152487052}", //1000
            "{\"temperature\":25.2,\"timestamp\":1541152487062}", //1200
            "{\"temperature\":26.5,\"timestamp\":1541152487072}", //1400
            "{\"temperature\":27.1,\"timestamp\":1541152487082}", //1600
            "{\"temperature\":27.6,\"timestamp\":1541152487092}" //1800
    )));
    int qos = 2;
    String broker = "tcp://192.168.0.2:1883";
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