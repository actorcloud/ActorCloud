package io.emqx.stream.agent;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NonNull;

import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
public class Rule {
  @NonNull
  private String id;
  @NonNull
  private String sql;
  @NonNull
  private List<Map<String, Object>> actions;
  private boolean enabled;
}