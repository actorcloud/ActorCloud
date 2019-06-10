package io.emqx.stream.common.sql.visitor;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.GeoUtils;
import io.emqx.stream.common.sql.SqlExecutionContext;
import net.sf.jsqlparser.expression.*;
import net.sf.jsqlparser.expression.operators.arithmetic.*;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;
import net.sf.jsqlparser.expression.operators.conditional.OrExpression;
import net.sf.jsqlparser.expression.operators.relational.*;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.select.SubSelect;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Stack;

/**
 * The visitor to evaluate the value of a expression
 */
public class ExpressionEvaluator extends ExpressionVisitorAdapter {
  private Map<String, Object> record;
  //For aggregate function evaluations
  private List<Map<String, Object>> records;
  private Map<String, List<Map<String, Object>>> groups;
  private SqlExecutionContext context;

  // operands can only be the supported primitive data types: long(bigint), float(double), string, datetime, boolean and null
  private Stack<Object> operands = new Stack<>();

  private static final int OR = 1;
  private static final int AND = 11;
  private static final int EQU = 21;
  private static final int NEQ = 22;
  private static final int GT = 23;
  private static final int GTE = 24;
  private static final int LT = 25;
  private static final int LTE = 26;
  private static final int ADD = 31;
  private static final int SUB = 32;
  private static final int MUL = 41;
  private static final int DIV = 42;
  private static final int MOD = 51;

  public Object evaluate(Expression exp, Map<String, Object> record, SqlExecutionContext context){
    operands = new Stack<>();
    this.context = context;
    this.record = record;
    this.records = context.records();
    this.groups = context.groups();
    exp.accept(this);
    return operands.pop();
  }

  /**
   * Evaluate simple expression that needs no context
   */
  public Object evaluate(final Expression exp){
    exp.accept(this);
    return operands.pop();
  }

  @Override
  public void visit(NullValue value) {
    operands.push(null);
  }

  @Override
  public void visit(DoubleValue value) {
    operands.push(value.getValue());
  }

  @Override
  public void visit(LongValue value) {
    operands.push(value.getValue());
  }

  //TODO deal with datetime
  @Override
  public void visit(DateValue value) {
    operands.push(value.getValue());
  }

  @Override
  public void visit(TimeValue value) {
    operands.push(value.getValue());
  }

  @Override
  public void visit(TimestampValue value) {
    operands.push(value.getValue());
  }

  @Override
  public void visit(StringValue value) {
    operands.push(value.getValue());
  }

  @Override
  public void visit(Column column) {
    Table table = column.getTable();
    String tableName = null;
    if(table != null && table.getName() != null){
      tableName = table.getAlias() != null ? table.getAlias().getName() : table.toString();
    }
    Object value = getColValue(column.getColumnName(), tableName);
    operands.push(value);
  }

  private Object getColValue(String columnName, String tableName) {
    if(record == null){
      return null;
    }
    Object value;
    Map<String, Object> flatRecord = null;
    String[] colNames = columnName.split(Constants.RECORD_FIELD_SEPERATOR);
    String firstColName = colNames[0];
    if((boolean)record.getOrDefault(Constants.JOIN_FIELD, false)) {
      flatRecord = flatJoinedRecord(tableName, record, firstColName);
    }else if(context.lateralRow() != null){
      flatRecord = flatJoinedRecord(tableName, context.lateralRow(), firstColName);
    }
    value = flatRecord == null ? record : flatRecord;
    for(String colName:colNames){
      try{
        if(value instanceof Map){
          //noinspection unchecked
          value = ((Map<String, Object>) value).get(colName);
        }else if(value instanceof List){
          value = ((List) value).get(Integer.parseInt(colName));
        }else{
          throw new RuntimeException(String.format("Cannot read the column %s.%s", tableName, columnName));
        }
      }catch(Exception exp){
        throw new RuntimeException(String.format("Cannot read the column %s.%s", tableName, columnName),exp);
      }
    }
    return value;
  }

  private Map<String, Object> flatJoinedRecord(String tableName, Map<String, Object> parentRecord, String firstColName) {
    Map<String, Object> flatRecord = null;
    if(tableName != null) {
      //noinspection unchecked
      flatRecord = (Map<String, Object>) parentRecord.get(tableName);
    }else {
      //TODO with schema this can be inferred
      for(Object topic: parentRecord.values()){
        try{
          @SuppressWarnings("unchecked") Map<String, Object> topicMap = (Map<String, Object>) topic;
          if(topicMap.containsKey(firstColName)) {
            flatRecord = topicMap;
            break;
          }
        }catch(Exception ex){
          //do nothing for non topic value
        }
      }
    }
    return flatRecord;
  }

  @Override
  public void visit(Function function) {
    Object value = null;
    //TODO refactor to visitor
    String functionName = function.getName().toLowerCase();
    List<Expression> params = function.getParameters() != null ? function.getParameters().getExpressions() : new ArrayList<>();
    switch(functionName){
      case "count":
        if(!function.isAllColumns() && params.size() != 1){
          throw new RuntimeException("Invalid parameters for function " + functionName);
        }
        long count;
        if(record == null){
          count = 0;
        }else{
          //Expression param = params.get(0);
          String group = (String) record.get(Constants.GROUP);
          // if(group != null && param instanceof Column){
          //   //TODO any difference？
          // }else{
          if(group != null){
            count = groups.get(group).size();
          }else{
            count = records.parallelStream().filter(record ->
                    (boolean)record.getOrDefault(Constants.PASSWHERE, false) || (boolean)record.getOrDefault(Constants.CONDITION, true))
                    .count();
          }
        }
        value = count;
        // }
        break;
      case "avg":
        break;
      case "lag":
        if(params.size() != 1){
          throw new RuntimeException("Invalid parameters for function " + functionName);
        }
        Map<String, Object> lagRow = getLastRow();
        if(lagRow != null){
          value = getCol(lagRow, ((Column)params.get(0)).getColumnName());
        }else{
          value = null;
        }
        break;
      case "size":
        value = (long)context.records().size();
        break;
      case "getmetadatapropertyvalue":
        if(params.size() != 2){
          throw new RuntimeException("Invalid parameters for function " + functionName);
        }
        params.get(0).accept(this);
        String topicName = (String) operands.pop();
        params.get(1).accept(this);
        String metaName = (String) operands.pop();
        if(metaName.equalsIgnoreCase("topic")){
          value = getColValue(Constants.TOPIC_FIELD, topicName);
        }else{
          throw new RuntimeException("Invalid parameters for function " + functionName);
        }
        break;
      case Constants.TUMBLINGWINDOW:
      case Constants.HOPPINGWINDOW:
      case Constants.SLIDINGWINDOW:
      case Constants.SESSIONWINDOW:
        value = null;  //TODO Should only allow on group by
        break;
      case "ftoc":
        if(params.size() == 1 && params.get(0) instanceof Column){
          params.get(0).accept(this);
          Object colValue = operands.pop();
          double fahrenheit;
          if(colValue instanceof Long){
            fahrenheit = (long) colValue;
          }else if (colValue instanceof Integer) {
            fahrenheit = ((Integer) colValue).longValue();
          }else if(colValue instanceof Double){
            fahrenheit = (double) colValue;
          }else {
            throw new RuntimeException("ftoc parameter is invalid");
          }
          value = ( 5 *(fahrenheit - 32.0)) / 9.0;
        }
        break;
      case "ctof":
        if(params.size() == 1 && params.get(0) instanceof Column){
          params.get(0).accept(this);
          Object colValue = operands.pop();
          double celsius;
          if(colValue instanceof Long){
            celsius = (long) colValue;
          }else if (colValue instanceof Integer) {
            celsius = ((Integer) colValue).longValue();
          }else if(colValue instanceof Double){
            celsius = (double) colValue;
          }else {
            throw new RuntimeException("ftoc parameter is invalid");
          }
          value = celsius * 1.8 + 32;
        }
        break;
      case "incircle":
          if (params.size() != 5) {
              throw new RuntimeException("Invalid parameters for function " + functionName);
          }
          double lat = (double) evaluate(params.get(0));
          double lng = (double) evaluate(params.get(1));
          double lat1 = (double) evaluate(params.get(2));
          double lng1 = (double) evaluate(params.get(3));
          double radius = Double.parseDouble(params.get(4).toString());
          value = GeoUtils.isInCircle(lat, lng, lat1, lng1, radius);
          break;
      case "inpolygon":
          if (params.size() != 3) {
              throw new RuntimeException("Invalid parameters for function " + functionName);
          }
          double lat2 = (double) evaluate(params.get(0));
          double lng2 = (double) evaluate(params.get(1));
          String pointArrayStr = (String) evaluate(params.get(2));
          value = GeoUtils.isInPolygon(lat2, lng2, pointArrayStr);
          break;
      case "split_part":
        if (params.size() != 3) {
          throw new RuntimeException("Invalid parameters for function " + functionName);
        }
        String text = ((String) evaluate(params.get(0)));
        String delimiter = ((String) evaluate(params.get(1)));
        long position = (long) evaluate(params.get(2));
        String[] result = text.split(delimiter);
        if (position <= 0 || position > result.length) {
          value = "";
        } else {
          value = result[((int) position) - 1];
        }
        break;
      default:
        throw new RuntimeException("Unsupported function " + functionName);
    }
    operands.push(value);
  }

  private Map<String, Object> getLastRow() {
    for(int i=0;i<records.size();i++){
      if(record == records.get(i)){
        if(i==0) break;
        return records.get(i-1);
      }
    }
    if(context.lastRecords() != null && !context.lastRecords().isEmpty()){
      return context.lastRecords().get(context.lastRecords().size() - 1);
    }
    return null;
  }

  private Object getCol(Map<String, Object> row, String col) {
    String[] colNames = col.split(Constants.RECORD_FIELD_SEPERATOR);
    Object result = row;
    for(String colName:colNames){
      result = ((Map) result).get(colName);
    }
    return result;
  }

  @Override
  public void visit(Addition expr) {
    visitBinaryExpression(expr, ADD);
  }

  @Override
  public void visit(Division expr) {
    visitBinaryExpression(expr, DIV);
  }

  @Override
  public void visit(Multiplication expr) {
    visitBinaryExpression(expr, MUL);
  }

  @Override
  public void visit(Subtraction expr) {
    visitBinaryExpression(expr, SUB);
  }

  @Override
  public void visit(Modulo expr) {
    visitBinaryExpression(expr, MOD);
  }

  @Override
  public void visit(AndExpression expr) {
    visitBinaryExpression(expr, AND);
  }

  @Override
  public void visit(Parenthesis parenthesis) {
    parenthesis.getExpression().accept(this);
    if(parenthesis.isNot()){
      Object result = operands.pop();
      if(result instanceof Boolean){
        operands.push(!(boolean)result);
      }else{
        throw new RuntimeException("Unsupported operator 'NOT' on non-boolean value");
      }
    }
  }

  @Override
  public void visit(OrExpression expr) {
    visitBinaryExpression(expr, OR);
  }

  @Override
  public void visit(Between expr) {
    throw new RuntimeException("Between operator is to be supported");
//    expr.getLeftExpression().accept(this);
//    expr.getBetweenExpressionStart().accept(this);
//    expr.getBetweenExpressionEnd().accept(this);
  }

  @Override
  public void visit(EqualsTo expr) {
    visitBinaryExpression(expr, EQU);
  }

  @Override
  public void visit(GreaterThan expr) {
    visitBinaryExpression(expr, GT);
  }

  @Override
  public void visit(GreaterThanEquals expr) {
    visitBinaryExpression(expr, GTE);
  }

  @Override
  public void visit(InExpression expr) {
    if(expr.getLeftItemsList() != null){
      throw new RuntimeException("In operator with left item list is to be supported");
    }
    expr.getLeftExpression().accept(this);
    expr.getRightItemsList().accept(this);
    Object right = operands.pop();
    Object left = operands.pop();
    if(right instanceof List){
      boolean result = ((List) right).contains(left);
      if(expr.isNot()){
        result = !result;
      }
      operands.push(result);
    }else{
      throw new RuntimeException(String.format("Incompatible right item list %s for in expression", right));
    }
  }

  @Override
  public void visit(IsNullExpression expr) {
    throw new RuntimeException("IsNull operator is to be supported");
//    expr.getLeftExpression().accept(this);
  }

  @Override
  public void visit(LikeExpression expr) {
    throw new RuntimeException("like operator is to be supported");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(MinorThan expr) {
    visitBinaryExpression(expr, LT);
  }

  @Override
  public void visit(MinorThanEquals expr) {
    visitBinaryExpression(expr, LTE);
  }

  @Override
  public void visit(NotEqualsTo expr) {
    visitBinaryExpression(expr, NEQ);
  }

  @Override
  public void visit(SubSelect subSelect) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(CaseExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(WhenClause expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(ExistsExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(AllComparisonExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(AnyComparisonExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(Concat expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(Matches expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(BitwiseAnd expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(BitwiseOr expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(BitwiseXor expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(CastExpression expr) {
    throw new RuntimeException("Not supported expression");
//    expr.getLeftExpression().accept(this);
  }

  @Override
  public void visit(AnalyticExpression expr) {
    throw new RuntimeException("Not supported expression");
//    expr.getExpression().accept(this);
//    expr.getDefaultValue().accept(this);
//    expr.getOffset().accept(this);
//    for (OrderByElement element : expr.getOrderByElements()) {
//        element.getExpression().accept(this);
//    }
//
//    expr.getWindowElement().getRange().getStart().getExpression().accept(this);
//    expr.getWindowElement().getRange().getEnd().getExpression().accept(this);
//    expr.getWindowElement().getOffset().getExpression().accept(this);
  }

  @Override
  public void visit(ExtractExpression expr) {
    throw new RuntimeException("Not supported expression");
//    expr.getExpression().accept(this);
  }

  @Override
  public void visit(IntervalExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(OracleHierarchicalExpression expr) {
    throw new RuntimeException("Not supported expression");
  }

  @Override
  public void visit(RegExpMatchOperator expr) {
    throw new RuntimeException("Not supported expression");
//    visitBinaryExpression(expr);
  }

  @Override
  public void visit(ExpressionList expressionList) {
    List<Object> values = new ArrayList<>();
    for (Expression expr : expressionList.getExpressions()) {
        expr.accept(this);
        values.add(operands.pop());
    }
    operands.push(values);
  }

  @Override
  public void visit(MultiExpressionList multiExprList) {
    List<List<Object>> values = new ArrayList<>();
    for (ExpressionList list : multiExprList.getExprList()) {
        visit(list);
      //noinspection unchecked
      values.add((List<Object>) operands.pop());
    }
    operands.push(values);
  }

  private void visitBinaryExpression(BinaryExpression expr, int operator) {
    expr.getLeftExpression().accept(this);
    expr.getRightExpression().accept(this);
    Object right = operands.pop();
    Object left = operands.pop();
    switch(operator){
      case ADD:
      case SUB:
      case MUL:
      case DIV:
      case MOD:
        operands.push(doArithmetic(left, right, operator));
        break;
      case EQU:
      case NEQ:
      case GT:
      case GTE:
      case LT:
      case LTE:
        operands.push(doCompare(left, right, operator));
        break;
      case AND:
      case OR:
        operands.push(doRelation(left, right, operator));
        break;
      default:
        throw new RuntimeException("Unsupported operator");
    }
  }

  private Object doArithmetic(Object left, Object right, int operator) {
    Object value;
    if(left instanceof String && right instanceof String){
      value = doArithmetic((String)left, (String)right, operator);
    }else if(left instanceof Long){
      value = doArithmetic((long)left, right, operator);
    }else if(left instanceof Integer){
      value = doArithmetic(((Integer) left).longValue(), right, operator);
    }else if(left instanceof Double){
      value = doArithmetic((double)left, right, operator);
    }else {//TODO datetime
      throw new RuntimeException("Incompatible type for arithmetic");
    }
    return value;
  }

  private String doArithmetic(String left, String right, int operator) {
    if (operator == ADD) {
      return left + right;
    }
    throw new RuntimeException("Incompatible type for arithmetic");
  }

  private Object doArithmetic(long left, Object right, int operator) {
    if(right instanceof Long){
      return doArithmetic(left, (long)right, operator);
    }else if(right instanceof Integer){
      return doArithmetic(left, ((Integer) right).longValue(), operator);
    }else if(right instanceof Double){
      return doArithmetic(((Long)left).doubleValue(), (double)right, operator);
    }
    throw new RuntimeException("Incompatible type for arithmetic");
  }

  private Object doArithmetic(double left, Object right, int operator) {
    if(right instanceof Long){
      return doArithmetic(left, ((Long)right).doubleValue(), operator);
    }else if(right instanceof Integer){
      return doArithmetic(left, ((Integer) right).doubleValue(), operator);
    }else if(right instanceof Double){
      return doArithmetic(left, (double)right, operator);
    }
    throw new RuntimeException("Incompatible type for arithmetic");
  }

  private long doArithmetic(long left, long right, int operator) {
    switch(operator){
      case ADD:
        return left + right;
      case SUB:
        return left - right;
      case MUL:
        return left * right;
      case DIV:
        return left / right;
      case MOD:
        return left % right;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private double doArithmetic(double left, double right, int operator) {
    switch(operator){
      case ADD:
        return left + right;
      case SUB:
        return left - right;
      case MUL:
        return left * right;
      case DIV:
        return left / right;
      case MOD:
        return left % right;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private boolean doCompare(Object left, Object right, int operator) {
    boolean value;
    if (left == null || right == null) {
      value = false;
    } else if (left instanceof Boolean && right instanceof Boolean) {
      value = doCompare((boolean) left, (boolean) right, operator);
    } else if (left instanceof String && right instanceof String) {
      value = doCompare((String) left, (String) right, operator);
    } else if (left instanceof Long) {
      value = doCompare((long) left, right, operator);
    } else if (left instanceof Integer) {
      value = doCompare(((Integer) left).longValue(), right, operator);
    } else if (left instanceof Double) {
      value = doCompare((double) left, right, operator);
    } else {
      throw new RuntimeException("Incompatible type for arithmetic");
    }
    return value;
  }

  private boolean doCompare(boolean left, Object right, int operator) {
    if(right instanceof Long || right instanceof Integer){
      boolean rightBoolean;
      int rightInt = (int)right;
      if(rightInt == 0){
        rightBoolean = false;
      }else if(rightInt == 1){
        rightBoolean = true;
      }else{
        throw new RuntimeException(String.format("Cannot compare %s and %s", left, right));
      }
      return doCompare(left, rightBoolean, operator);
    }else if(right instanceof Boolean){
      return doCompare(left, (boolean)right, operator);
    }
    throw new RuntimeException(String.format("Cannot compare %s and %s", left, right));
  }

  private boolean doCompare(boolean left, boolean right, int operator) {
    switch(operator){
      case EQU:
        return left == right;
      case NEQ:
        return left != right;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private boolean doCompare(String left, String right, int operator) {
    switch(operator){
      case EQU:
        return left.equals(right);
      case NEQ:
        return !left.equals(right);
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private boolean doCompare(long left, Object right, int operator) {
    if(right instanceof Long){
      return doCompare(left, (long)right, operator);
    } else if (right instanceof Integer) {
      return doCompare(left, ((Integer) right).longValue(), operator);
    }else if(right instanceof Double){
      return doCompare(((Long)left).doubleValue(), (double)right, operator);
    }
    throw new RuntimeException("Incompatible type for arithmetic");
  }

  private boolean doCompare(double left, Object right, int operator) {
    if(right instanceof Long){
      return doCompare(left, ((Long)right).doubleValue(), operator);
    } else if (right instanceof Integer) {
      return doCompare(left, ((Integer) right).doubleValue(), operator);
    }else if(right instanceof Double){
      return doCompare(left, (double)right, operator);
    }
    throw new RuntimeException("Incompatible type for arithmetic");
  }

  private boolean doCompare(long left, long right, int operator) {
    switch(operator){
      case EQU:
        return left == right;
      case NEQ:
        return left != right;
      case GT:
        return left > right;
      case GTE:
        return left >= right;
      case LT:
        return left < right;
      case LTE:
        return left <= right;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private boolean doCompare(double left, double right, int operator) {
    int compareResult = Double.compare(left, right);
    switch(operator){
      case EQU:
        return compareResult == 0;
      case NEQ:
        return compareResult != 0;
      case GT:
        return compareResult > 0;
      case GTE:
        return compareResult >= 0;
      case LT:
        return compareResult < 0;
      case LTE:
        return compareResult <= 0;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }

  private boolean doRelation(Object left, Object right, int operator) {
    boolean value;
    if(left instanceof Boolean && right instanceof Boolean) {
      value = doRelation((boolean) left, (boolean) right, operator);
    }else{
      throw new RuntimeException("Incompatible type for relation");
    }
    return value;
  }

  private boolean doRelation(boolean left, boolean right, int operator) {
    switch(operator){
      case AND:
        return left && right;
      case OR:
        return left || right;
      default:
        throw new RuntimeException("Incompatible type for arithmetic");
    }
  }
}