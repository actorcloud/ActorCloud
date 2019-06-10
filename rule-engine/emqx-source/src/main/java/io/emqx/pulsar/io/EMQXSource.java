package io.emqx.pulsar.io;

import io.emqx.stream.common.Constants;
import lombok.Data;
import org.apache.pulsar.functions.api.Record;

import java.util.Optional;

public class EMQXSource extends AbstractEMQXSource<String> {
  @Override
  protected void doConsume(String topic, String message, long time) {
    consume(new StringRecord(Optional.of(randomString()), String.format("%s%s%s%s%d", topic,
            Constants.MESSAGE_SEPERATOR, message, Constants.MESSAGE_SEPERATOR, time)) );
  }

  @Data
  static private class StringRecord implements Record<String> {
    @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
    private final Optional<String> key;
    private final String value;
  }
}