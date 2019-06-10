package io.emqx.stream.agent.analyzer;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

import java.util.List;

@NoArgsConstructor
@Accessors(fluent = true) @Data
public class RuleFeature {
  private List<String> topics;
  private int windowType; //0 none, 1 duration 2 count 3 session
  private long windowLength;
  private long windowInterval;
}
