package io.emqx.pulsar.functions;

import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Run SQL engine against the message in String format.
 * The message will contain both meta data and real payload
 * Example: {"tenantId": "mytenant", "productId": 123, "payload":"{\"temp\":23.4}"}
 */
public class StringRuleFunction extends AbstractRuleFunction implements Function<String, Void> {

  @Override
  public Void process(String topicMessage, Context context) throws Exception {
    List<Map<String,Object>> inputs = new ArrayList<>();
    inputs.add(topicMessageToMap(topicMessage, context.getLogger()));
    return super.process(inputs, context);
  }
}
