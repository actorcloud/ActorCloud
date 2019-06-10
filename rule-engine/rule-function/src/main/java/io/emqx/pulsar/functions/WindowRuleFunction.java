package io.emqx.pulsar.functions;

import java.util.Collection;
import java.util.stream.Collectors;

import org.apache.pulsar.client.api.schema.GenericRecord;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;

public class WindowRuleFunction extends AbstractRuleFunction implements Function<Collection<GenericRecord>, Void> {

  @Override
  public Void process(Collection<GenericRecord> inputs, Context context) throws Exception {
    return super.process(inputs.parallelStream().map(this::genericRecordToMap).collect(Collectors.toList()), context);
  }
}
