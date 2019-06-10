package io.emqx.pulsar.functions;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.pulsar.client.api.schema.GenericRecord;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;

public class RuleFunction extends AbstractRuleFunction implements Function<GenericRecord, Void> {

  @Override
  public Void process(GenericRecord input, Context context) throws Exception {
    List<Map<String,Object>> inputs = new ArrayList<>();
    inputs.add(genericRecordToMap(input));
    return super.process(inputs, context);
  }
}
