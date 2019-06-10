package client.actorCloud;

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

public class MqttPublish {

  public static void main(String[] args) {

    String broker = args[0];
    Map<String, List<String>> messages = new HashMap<>();
    messages.put("actorcloud", new ArrayList<>(Arrays.asList(
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":65.05,\"temp\":24.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485022}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":64.27,\"temp\":24.16},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485220}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":64.04,\"temp\":24.12},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485418}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":63.83,\"temp\":24.1},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485612}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":64.35,\"temp\":24.01},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485808}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":64.66,\"temp\":24.05},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486002}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":65.3,\"temp\":24.0},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486200}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":64.31,\"temp\":15.7},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486398}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":62.69,\"temp\":15.53},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486596}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":16.64,\"temp\":15.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486790}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":62.93,\"temp\":22.92},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486988}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":63.66,\"temp\":15.12},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487186}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":63.81,\"temp\":15.53},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487379}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":62.79,\"temp\":24.04},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487575}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":16.49,\"temp\":24.55},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487771}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":63.5,\"temp\":24.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487969}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":63.64,\"temp\":24.05},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488168}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":65.03,\"temp\":15.92},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488363}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":65.95,\"temp\":15.84},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488558}",
            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"device_id_1\",\"qos\":1.0,"
                    + "\"payload\":{\"hum\":67.38,\"temp\":15.51},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488777}"
    )));
    int qos = 2;

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
