package io.emqx.pulsar.functions;

import java.util.Collection;

public class DummyWindowFunction implements java.util.function.Function<Collection<String>, Void> {
  @Override
  public Void apply(Collection<String> topicMessages) {
    return null;
  }
}
