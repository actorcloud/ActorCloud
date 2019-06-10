package io.emqx.stream.common.sql;

import io.emqx.stream.common.Constants;
import lombok.Data;
import lombok.experimental.Accessors;

import java.util.List;

@Accessors(fluent = true) @Data
public class SqlFunction {
  private String name;
  private List<Constants.ValidateStage> stages;
  private List<Class> arguments;
  private Class returnType;
  private String description;
}
