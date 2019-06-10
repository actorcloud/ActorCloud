package io.emqx.pulsar.io;

import io.emqx.stream.common.JsonParser;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.io.core.Sink;
import org.apache.pulsar.io.core.SinkContext;
import org.eclipse.paho.client.mqttv3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

public class EMQXSink implements Sink<String> {

    private static final Logger logger = LoggerFactory.getLogger(EMQXSink.class);
    private SinkConfig sinkConfig;
    private String clientId;
    private MqttClient client;
    private MqttConnectOptions conOpt;

    @Override
    public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {
        sinkConfig = SinkConfig.load(config);
        if (sinkConfig.getBrokerUrl() == null) {
            throw new IllegalArgumentException("Required property not set.");
        }
        clientId = "pulsarIOSink_mqtt_forward";

        // Construct the connection options object that contains connection parameters
        // such as cleanSession and LWT
        conOpt = new MqttConnectOptions();

        connect();
    }

    private void connect() throws MqttException {
        // Construct an MQTT blocking mode client
        client = new MqttClient(sinkConfig.getBrokerUrl(), clientId);

        // Set this wrapper as the callback handler
        client.setCallback(new SinkCallback());
        // Connect to the MQTT server
        client.connect(conOpt);
        logger.info("Connected to {} with client ID {}", sinkConfig.getBrokerUrl(), client.getClientId());

    }

    @Override
    public void write(Record<String> record) throws Exception {
        while (client == null) {
            try {
                connect();
            } catch (Exception exp) {
                logger.error("Reconnect error", exp);
                client = null;
                Thread.sleep(500);
            }
        }

        String message = record.getValue();
        logger.info("EMQXSink received message: {} ", message);
        Map<String, Object> actionMessage = JsonParser.parseMqttMessage(message);
        assert actionMessage != null;
        //noinspection unchecked
        Map<String, Object> action = (Map<String, Object>) actionMessage.get("action");
        String outputTopic = ((String) action.get("topic"));
        //noinspection unchecked
        List<Map<String, Object>> values = (List<Map<String, Object>>) actionMessage.get("values");
        if (!values.isEmpty()) {
            // Forward the first result of the value list
            Map<String, Object> result = values.get(0);
            String payload = JsonParser.toJson(result);
            MqttMessage mqttMessage = new MqttMessage(payload.getBytes());
            client.publish(outputTopic, mqttMessage);
            record.ack();
        }
    }

    @Override
    public void close() throws Exception {
        if (client != null) {
            client.disconnect();
        }
    }

    class SinkCallback implements MqttCallback {

        @Override
        public void connectionLost(Throwable cause) {
            logger.info("Connection to {} lost! {}", sinkConfig.getBrokerUrl(), cause);
            client = null;
            cause.printStackTrace();
        }

        @Override
        public void messageArrived(String topic, MqttMessage message) {

        }

        @Override
        public void deliveryComplete(IMqttDeliveryToken token) {

        }

    }
}


