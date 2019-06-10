package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.visitor.ExpressionFilter;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class FilterPlan extends PlanAdaptor{
  private Expression expression;
  private boolean isHaving;

  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    context = super.execute(context);
    ExpressionFilter expFilter = new ExpressionFilter(context.logger());
    //filter having
    if(isHaving){
      if(context.groups() != null){
        context.groups(expFilter.filterHaving(expression, context));
      }else{
        context.records(expFilter.filterHavingNoGroup(expression, context));
      }
    }else{
      if(context.joins() != null){ //filter multiple from
        context.joins(expFilter.filterWhere(expression, context));
      }else{ //filter common where
        context.records(expFilter.filterWhere(expression, context));
      }
    }
    return context;
  }

  public void addCondition(Expression expr){
    if(expr != null){
      if(expression == null){
        expression = expr;
      }else{
        expression = new AndExpression(expression, expr);
      }
    }
  }
}
