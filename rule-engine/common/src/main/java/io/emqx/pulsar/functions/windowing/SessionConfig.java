package io.emqx.pulsar.functions.windowing;

import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import lombok.experimental.Accessors;

@Data
@Setter
@Getter
@Accessors(chain = true)
@ToString
public class SessionConfig {
  private Long windowLengthDurationMs;
  private Long timeoutlDurationMs;
}
