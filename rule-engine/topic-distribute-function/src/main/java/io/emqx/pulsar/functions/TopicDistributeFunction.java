package io.emqx.pulsar.functions;

import io.emqx.stream.common.Constants;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;

/**
 *  Predefined function for redistributing EMQX messages into multiple pulsar topics
 *  The input topic must be the output topic of the AC EMQX source
 *
 *  This function just redistribute the emqx topic as a pulsar topic.
 */
public class TopicDistributeFunction implements Function<String, Void> {
  @Override
  public Void process(String message, Context context) {
    String[] messages = message.split(Constants.MESSAGE_SEPERATOR);
    if(messages.length == 3){
      String topic = messages[0].replaceAll("/", "%%");
      context.getLogger().info("Publish to topic {}", topic);
      context.publish(topic, message);
    }else{
      context.getLogger().error("Invalid input message {}", message);
    }
    return null;
  }
}
