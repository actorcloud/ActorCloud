package io.emqx.stream.common.internal;

import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import io.emqx.stream.common.JsonParser;
import org.apache.pulsar.client.api.schema.Field;
import org.apache.pulsar.client.api.schema.GenericRecord;

public class MockGenericRecord implements GenericRecord {
  private final Map<String, Object> map;

  public MockGenericRecord(String json) {
    map = JsonParser.parseMqttMessage(json);
  }

  public MockGenericRecord(Map<String, Object> map) {
    this.map = map;
  }

  @Override
  public Object getField(String fieldName) {
    return map.get(fieldName);
  }

  @Override
  public List<Field> getFields() {
    List<Field> results = new LinkedList<>();
    int i = 0;
    for(String key: map.keySet()) {
      results.add(new Field(key, i));
      i++;
    }
    return results;
  }

}
