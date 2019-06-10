package io.emqx.stream.common.sql.pojo;

import io.emqx.stream.common.Constants;
import lombok.Data;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.statement.select.SubSelect;

import java.util.List;

@Accessors(fluent = true) @Data
public class JoinCondition {
  private Constants.JoinType type;
  private List<Tuple<String, String>> equivalents;
  private SubSelect lateral;
}
