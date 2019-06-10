package io.emqx.stream.common.sql.pojo;

import io.emqx.stream.common.Constants.WindowType;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

@NoArgsConstructor
@Accessors(fluent = true) @Data
public class Window {
  private WindowType type;
  private boolean isDuration;
  private long size;
  //Set to 0 if no slide window
  private long hopSize;
}
