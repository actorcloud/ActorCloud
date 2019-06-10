package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.sql.SqlExecutionContext;
import lombok.Data;
import lombok.experimental.Accessors;

@Accessors(fluent = true) @Data
public abstract class PlanAdaptor implements IPlan {
  protected IPlan dependant;
  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    if(dependant != null){
      context = dependant.execute(context);
    }
    return context;
  }
}
