package io.emqx.stream.common.sql.pojo;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.schema.Table;

@NoArgsConstructor
@Accessors(fluent = true) @Data
public class Selection {
  private boolean all;
  private int unnest; //0 is not, 1 is cross, 2 is outer
  private Table table;
  private Expression expression;
  private String outputName;
}
