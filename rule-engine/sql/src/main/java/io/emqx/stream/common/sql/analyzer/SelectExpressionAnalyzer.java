package io.emqx.stream.common.sql.analyzer;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.pojo.Selection;
import net.sf.jsqlparser.expression.*;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.statement.select.SubSelect;

import java.util.ArrayList;
import java.util.List;

class SelectExpressionAnalyzer extends ExpressionVisitorAdapter {
  private final Selection selection;
  
  public SelectExpressionAnalyzer(Selection selection){
    this.selection = selection;
  }

  @Override
  public void visit(Function function) {

    String functionName = function.getName().toLowerCase();
    List<Expression> params = function.getParameters() != null ? function.getParameters().getExpressions() : new ArrayList<>();
    if(functionName.equals("unnest")){
      if(params.size() < 1 || params.size() > 2){
        throw new RuntimeException("Invalid parameters for function " + functionName);
      }
      selection.expression(params.get(0)).unnest(Constants.CROSS_APPLY);
      if(params.size() == 2 && params.get(1) instanceof StringValue){
        String applyType = ((StringValue) params.get(1)).getValue();
        if(applyType.equalsIgnoreCase("cross")){
          selection.unnest(Constants.CROSS_APPLY);
        }else if(applyType.equalsIgnoreCase("outer")){
          selection.unnest(Constants.OUTER_APPLY);
        }else{
          throw new RuntimeException(String.format("Invalid parameter %s for function %s",applyType, functionName));
        }
      }
    }else{
      selection.expression(function);
    }
    selection.outputName(function.getName());
  }

  @Override
  public void visit(Column column) {
    selection.expression(column)
      .outputName(column.toString());
  }
  
  //TODO is this supported?
  @Override
  public void visit(SubSelect subSelect) {
      
  }

  //TODO for below value functions
  @Override
  public void visit(DoubleValue value) {

  }

  @Override
  public void visit(LongValue value) {

  }

  @Override
  public void visit(DateValue value) {

  }

  @Override
  public void visit(TimeValue value) {

  }

  @Override
  public void visit(TimestampValue value) {

  }

  @Override
  public void visit(StringValue value) {

  }

}