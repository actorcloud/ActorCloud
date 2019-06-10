package io.emqx.pulsar.functions;

import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

public class StringWindowRuleFunction extends AbstractRuleFunction implements Function<Collection<String>, Void> {

  @Override
  public Void process(Collection<String> topicMessages, Context context) throws Exception {
    List<Map<String, Object>> inputs = new ArrayList<>();
    for(String topicMessage : topicMessages) {
      inputs.add(topicMessageToMap(topicMessage, context.getLogger()));
    }
    return super.process(inputs, context);
  }
}
