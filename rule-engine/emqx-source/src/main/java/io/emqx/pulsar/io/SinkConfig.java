package io.emqx.pulsar.io;

import java.io.Serializable;
import java.util.Map;

import com.google.gson.Gson;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import lombok.experimental.Accessors;

@Data
@Setter
@Getter
@EqualsAndHashCode
@ToString
@Accessors(chain = true)
public class SinkConfig implements Serializable {
  private static final long serialVersionUID = 1L;

  private String brokerUrl = "tcp://localhost:1883";
  private String outputTopic;
  private String ruleId;

  public static SinkConfig load(Map<String, Object> map) {
    return new Gson().fromJson(new Gson().toJson(map), SinkConfig.class);
  }
}
