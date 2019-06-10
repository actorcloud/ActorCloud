package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.pojo.Window;
import io.emqx.stream.common.sql.visitor.Aggregator;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.expression.Expression;

import java.util.List;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class AggregatePlan extends PlanAdaptor {
  private List<Expression> expressions;
  private Window window;

  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    context = super.execute(context);
    if(!expressions.isEmpty()){
      Aggregator aggregator = new Aggregator();
      context.groups(aggregator.grouping(expressions, context));
    }
    return context;
  }
}
