package io.emqx.pulsar.io;

import com.google.gson.JsonSyntaxException;
import org.apache.pulsar.io.core.PushSource;
import org.apache.pulsar.io.core.SourceContext;
import org.eclipse.paho.client.mqttv3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Random;

/**
 * Read mqtt message and filter to the topic. 
 * Need to pass sourceConfig topic1;topic2
 * @author Administrator
 *
 */
@SuppressWarnings("unused")
abstract class AbstractEMQXSource<T> extends PushSource<T>{

  protected static final Logger logger = LoggerFactory.getLogger(AbstractEMQXSource.class);
  private MqttClient client;
  private EMQXConfig emqxConfig;
  private MqttConnectOptions conOpt;
  private String clientId;

  public void close() throws Exception {
    if(client != null) {
      client.disconnect();
    }
  }

  @Override
  public void open(Map<String, Object> config, SourceContext sourceContext) throws Exception {
    emqxConfig = EMQXConfig.load(config);
    if (emqxConfig.getRuleId() == null || emqxConfig.getBrokerUrl() == null
            || emqxConfig.getInputTopics() == null) {
      throw new IllegalArgumentException("Required property not set.");
    }
    clientId = emqxConfig.getClientId() != null ? emqxConfig.getClientId() : "pulsario_" + emqxConfig.getRuleId() + "_" + sourceContext.getInstanceId();

    // Construct the connection options object that contains connection parameters
    // such as cleanSession and LWT
    conOpt = new MqttConnectOptions();
    if(emqxConfig.getUserName() != null){
      conOpt.setUserName(emqxConfig.getUserName());
    }
    if(emqxConfig.getPassword() != null){
      conOpt.setPassword(emqxConfig.getPassword().toCharArray());
    }
    connect();
  }

  private void connect() throws MqttException {
    // Construct an MQTT blocking mode client
    client = new MqttClient(emqxConfig.getBrokerUrl(),clientId);

    // Set this wrapper as the callback handler
    client.setCallback(new SourceCallback());
    // Connect to the MQTT server
    client.connect(conOpt);
    logger.info("Connected to {} with client ID {}", emqxConfig.getBrokerUrl() , client.getClientId());

    String[] topics = emqxConfig.getInputTopics().split(";");
    // Subscribe to the requested topic
    // The QoS specified is the maximum level that messages will be sent to the client at.
    // For instance if QoS 1 is specified, any messages originally published at QoS 2 will
    // be downgraded to 1 when delivering to the client but messages published at 1 and 0
    // will be received at the same level they were published at.
    logger.info("Subscribing to topic {}", emqxConfig.getInputTopics());
    client.subscribe(topics);
  }

  protected abstract void doConsume(String topic, String message, long time);

  protected String randomString() {
    int leftLimit = 97; // letter 'a'
    int rightLimit = 122; // letter 'z'
    int targetStringLength = 10;
    Random random = new Random();
    StringBuilder buffer = new StringBuilder(targetStringLength);
    for (int i = 0; i < targetStringLength; i++) {
      int randomLimitedInt = leftLimit + (int)
              (random.nextFloat() * (rightLimit - leftLimit + 1));
      buffer.append((char) randomLimitedInt);
    }

    return buffer.toString();
  }

   @SuppressWarnings("unused")
  class SourceCallback implements MqttCallback {
    public void connectionLost(Throwable cause) {
      // Called when the connection to the server has been lost.
      // An application may choose to implement reconnection
      // logic at this point. This sample simply exits.
      logger.info("Connection to {} lost! {}", emqxConfig.getBrokerUrl(), cause);
      cause.printStackTrace();
      try {
        Thread.sleep(500);
        connect();
      } catch (MqttException e) {
        e.printStackTrace();
        System.exit(1);
      } catch (InterruptedException ignored) {
      }
    }

    @SuppressWarnings("RedundantThrows")
    public void messageArrived(String topic, MqttMessage message) throws Exception {
      // Called when a message arrives from the server that matches any
      // subscription made by the client
      long time = System.currentTimeMillis();
      String messageStr = new String(message.getPayload());
      logger.debug("Time:\t" +time +
              "  Topic:\t" + topic +
              "  Message:\t" + messageStr +
              "  QoS:\t" + message.getQos());
      try {
        doConsume(topic, messageStr, time);
      } catch(JsonSyntaxException exp) {
        logger.error("Error happend while reading message: {} from topic: {}", messageStr, topic);
        exp.printStackTrace();
      }
    }

    public void deliveryComplete(IMqttDeliveryToken token) {


    }
  }
}


