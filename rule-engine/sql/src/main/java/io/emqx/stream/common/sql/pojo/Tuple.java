package io.emqx.stream.common.sql.pojo;

import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.experimental.Accessors;

@RequiredArgsConstructor
@Accessors(fluent = true) @Data
public class Tuple<X, Y> {
  private final X left;
  private final Y right;
}
