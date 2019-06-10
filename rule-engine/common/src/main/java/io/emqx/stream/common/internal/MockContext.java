package io.emqx.stream.common.internal;

import java.nio.ByteBuffer;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Record;
import org.slf4j.Logger;

import lombok.Data;
import lombok.NonNull;

@Data
@NoArgsConstructor
@RequiredArgsConstructor
public class MockContext implements Context {
  @NonNull
  private Map<String, Object> userConfigMap;
  private String result;
  private String resultTopic;
  private Map<String, ByteBuffer> state = new HashMap<>();
  private Record<?> record;

  public void clean() {
    result = null;
    resultTopic = null;
  }

  @Override
  public void incrCounter(String key, long amount) {


  }

  @Override
  public long getCounter(String key) {

    return 0;
  }

  @Override
  public void putState(String key, ByteBuffer value) {
    state.put(key, value);
  }

  @Override
  public ByteBuffer getState(String key) {
    return state.get(key);
  }

  @Override
  public Optional<Object> getUserConfigValue(String key) {
    return Optional.ofNullable(userConfigMap.get(key));
  }

  @Override
  public Object getUserConfigValueOrDefault(String key, Object defaultValue) {
    return userConfigMap.getOrDefault(key, defaultValue);
  }

  @Override
  public <O> CompletableFuture<Void> publish(String topicName, O object) {
    this.resultTopic = topicName;
    if(this.result != null) {
      this.result += '\n' + object.toString();
    }else {
      this.result = object.toString();
    }

    return null;
  }

  @Override
  public Record<?> getCurrentRecord() {
    return record;
  }

  @Override
  public Collection<String> getInputTopics() {

    return null;
  }

  @Override
  public String getOutputTopic() {

    return null;
  }

  @Override
  public String getOutputSchemaType() {

    return null;
  }

  @Override
  public String getTenant() {

    return null;
  }

  @Override
  public String getNamespace() {

    return null;
  }

  @Override
  public String getFunctionName() {

    return null;
  }

  @Override
  public String getFunctionId() {
    return "rule1";
  }

  @Override
  public int getInstanceId() {

    return 0;
  }

  @Override
  public int getNumInstances() {

    return 0;
  }

  @Override
  public String getFunctionVersion() {

    return null;
  }

  @Override
  public Logger getLogger() {
    return new MockLogger();
  }

  @Override
  public void recordMetric(String metricName, double value) {


  }

  @Override
  public <O> CompletableFuture<Void> publish(String topicName, O object, String schemaOrSerdeClassName) {

    return null;
  }

}
