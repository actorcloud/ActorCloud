package io.emqx.stream.common.sql.validator;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlFunction;
import io.emqx.stream.common.sql.SqlFunctionProvider;
import net.sf.jsqlparser.expression.*;
import net.sf.jsqlparser.expression.operators.arithmetic.*;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;
import net.sf.jsqlparser.expression.operators.conditional.OrExpression;
import net.sf.jsqlparser.expression.operators.relational.*;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.select.*;

import java.util.*;

/**
 * Validate a sql select statement to make sure the syntax is supported for the current version
 */
public class StreamSqlValidator implements SelectVisitor, FromItemVisitor, ExpressionVisitor, ItemsListVisitor, SelectItemVisitor{

  private static final Map<String, SqlFunction> supportedFunctions = SqlFunctionProvider.getAllFunctions();

  private boolean multipleTopic = false;
  private Constants.ValidateStage stage;
  private boolean inWindow = false;
  /**
   * The entry method to validate a sql select statement
   * @param select The Sql select statement to be validated
   * @return true if validation success. Otherwise, a runtime exception will be thrown
   */
  @SuppressWarnings("SameReturnValue")
  public boolean validate(Select select) throws RuntimeException{
    return validate(select, false);
  }

  /**
   * The entry method to validate a sql select statement. It won't deduce if there are multiple topics, the caller must
   * calcuate and pass it.
   * @param select he Sql select statement to be validated
   * @param multipleTopic If the selet statement involves multiple topiccs. The topics can be gotten from tableNameFinder
   * @return true if validation success. Otherwise, a runtime exception will be thrown
   * @throws RuntimeException if vallidation fails
   */
  @SuppressWarnings("SameReturnValue")
  public boolean validate(Select select, boolean multipleTopic) throws RuntimeException{
    this.multipleTopic = multipleTopic;
    if (select.getWithItemsList() != null) {
      throw new RuntimeException("WITH is not supported yet");
    }
    select.getSelectBody().accept(this);
    return true;
  }

  private void visitBinaryExpression(BinaryExpression binaryExpression) {
    binaryExpression.getLeftExpression().accept(this);
    binaryExpression.getRightExpression().accept(this);
  }

  @Override
  public void visit(NullValue nullValue) {

  }

  @Override
  public void visit(Function function) {
    String functionName = function.getName().toLowerCase();
    if(!supportedFunctions.keySet().contains(functionName)){
      throw new RuntimeException(String.format("Function %s is not supported", function.getName()));
    }
    switch(functionName){
      case Constants.TUMBLINGWINDOW:
      case Constants.HOPPINGWINDOW:
      case Constants.SLIDINGWINDOW:
      case Constants.SESSIONWINDOW:
        inWindow = true;
        break;
      case "size":
        if(!inWindow){
          throw new RuntimeException("FUNCTION size can only be used in windowing");
        }
        break;
    }
    SqlFunction sqlFunc = supportedFunctions.get(functionName);
    List<Expression> params = function.getParameters() != null ? function.getParameters().getExpressions() : new ArrayList<>();
    int paramSize = params.size();
    if(function.isAllColumns()){
      paramSize += 1;
    }
    if(paramSize != sqlFunc.arguments().size()){
      throw new RuntimeException("Invalid parameters for function " + functionName);
    }
    if(!sqlFunc.stages().contains(stage)){
      throw new RuntimeException(String.format("FUNCTION %s cannot be used at %s", functionName, stage));
    }
  }

  @Override
  public void visit(SignedExpression signedExpression) {
    signedExpression.getExpression().accept(this);
  }

  @Override
  public void visit(JdbcParameter jdbcParameter) {
    throw new RuntimeException(String.format("Expression %s is not supported", jdbcParameter));
  }

  @Override
  public void visit(JdbcNamedParameter jdbcNamedParameter) {
    throw new RuntimeException(String.format("Expression %s is not supported", jdbcNamedParameter));
  }

  @Override
  public void visit(DoubleValue doubleValue) {

  }

  @Override
  public void visit(LongValue longValue) {

  }

  @Override
  public void visit(DateValue dateValue) {

  }

  @Override
  public void visit(TimeValue timeValue) {

  }

  @Override
  public void visit(TimestampValue timestampValue) {

  }

  @Override
  public void visit(Parenthesis parenthesis) {
    parenthesis.getExpression().accept(this);
  }

  @Override
  public void visit(StringValue stringValue) {

  }

  @Override
  public void visit(Addition addition) {
    visitBinaryExpression(addition);
  }

  @Override
  public void visit(Division division) {
    visitBinaryExpression(division);
  }

  @Override
  public void visit(Multiplication multiplication) {
    visitBinaryExpression(multiplication);
  }

  @Override
  public void visit(Subtraction subtraction) {
    visitBinaryExpression(subtraction);
  }

  @Override
  public void visit(AndExpression andExpression) {
    visitBinaryExpression(andExpression);
  }

  @Override
  public void visit(OrExpression orExpression) {
    visitBinaryExpression(orExpression);
  }

  @Override
  public void visit(Between between) {
    throw new RuntimeException(String.format("Expression %s is not supported", between));
  }

  @Override
  public void visit(EqualsTo equalsTo) {
    visitBinaryExpression(equalsTo);
  }

  @Override
  public void visit(GreaterThan greaterThan) {
    visitBinaryExpression(greaterThan);
  }

  @Override
  public void visit(GreaterThanEquals greaterThanEquals) {
    visitBinaryExpression(greaterThanEquals);
  }

  @Override
  public void visit(InExpression inExpression) {
    if(inExpression.getLeftItemsList() != null){
      throw new RuntimeException("In operator with left item list is to be supported");
    }
    inExpression.getLeftExpression().accept(this);
    inExpression.getRightItemsList().accept(this);
  }

  @Override
  public void visit(IsNullExpression isNullExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", isNullExpression));
  }

  @Override
  public void visit(LikeExpression likeExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", likeExpression));
  }

  @Override
  public void visit(MinorThan minorThan) {

  }

  @Override
  public void visit(MinorThanEquals minorThanEquals) {

  }

  @Override
  public void visit(NotEqualsTo notEqualsTo) {

  }

  @Override
  public void visit(Column tableColumn) {

  }

  @Override
  public void visit(CaseExpression caseExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", caseExpression));
  }

  @Override
  public void visit(WhenClause whenClause) {
    throw new RuntimeException(String.format("Expression %s is not supported", whenClause));
  }

  @Override
  public void visit(ExistsExpression existsExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", existsExpression));
  }

  @Override
  public void visit(AllComparisonExpression allComparisonExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", allComparisonExpression));
  }

  @Override
  public void visit(AnyComparisonExpression anyComparisonExpression) {
    throw new RuntimeException(String.format("Expression %s is not supported", anyComparisonExpression));
  }

  @Override
  public void visit(Concat concat) {
    throw new RuntimeException(String.format("Expression %s is not supported", concat));
  }

  @Override
  public void visit(Matches matches) {
    throw new RuntimeException(String.format("Expression %s is not supported", matches));
  }

  @Override
  public void visit(BitwiseAnd bitwiseAnd) {
    throw new RuntimeException(String.format("Expression %s is not supported", bitwiseAnd));
  }

  @Override
  public void visit(BitwiseOr bitwiseOr) {
    throw new RuntimeException(String.format("Expression %s is not supported", bitwiseOr));
  }

  @Override
  public void visit(BitwiseXor bitwiseXor) {
    throw new RuntimeException(String.format("Expression %s is not supported", bitwiseXor));
  }

  @Override
  public void visit(CastExpression cast) {
    throw new RuntimeException(String.format("Expression %s is not supported", cast));
  }

  @Override
  public void visit(Modulo modulo) {

  }

  @Override
  public void visit(AnalyticExpression aexpr) {
    throw new RuntimeException(String.format("Expression %s is not supported", aexpr));
  }

  @Override
  public void visit(ExtractExpression eexpr) {
    throw new RuntimeException(String.format("Expression %s is not supported", eexpr));
  }

  @Override
  public void visit(IntervalExpression iexpr) {
    throw new RuntimeException(String.format("Expression %s is not supported", iexpr));
  }

  @Override
  public void visit(OracleHierarchicalExpression oexpr) {
    throw new RuntimeException(String.format("Expression %s is not supported", oexpr));
  }

  @Override
  public void visit(RegExpMatchOperator rexpr) {
    throw new RuntimeException(String.format("Expression %s is not supported", rexpr));
  }

  @Override
  public void visit(ExpressionList expressionList) {
    for (Expression expression : expressionList.getExpressions()) {
      expression.accept(this);
    }
  }

  @Override
  public void visit(MultiExpressionList multiExprList) {
    for (ExpressionList exprList : multiExprList.getExprList()) {
      exprList.accept(this);
    }
  }

  @Override
  public void visit(Table tableName) {

  }

  @Override
  public void visit(SubSelect subSelect) {
    subSelect.getSelectBody().accept(this);
  }

  @Override
  public void visit(SubJoin subjoin) {
    throw new RuntimeException(String.format("Subjoin %s is not supported", subjoin));
  }

  @Override
  public void visit(LateralSubSelect lateralSubSelect) {
    lateralSubSelect.getSubSelect().getSelectBody().accept(this);
  }

  @Override
  public void visit(ValuesList valuesList) {

  }

  @Override
  public void visit(PlainSelect plainSelect) {
    if(plainSelect.getInto() != null){
      throw new RuntimeException("INTO is not supported");
    }
    if(plainSelect.getDistinct() != null){
      throw new RuntimeException("DISTINCT is not supported");
    }
    if(plainSelect.getLimit() != null){
      throw new RuntimeException("LIMIT is not supported");
    }
    if(plainSelect.getOracleHierarchical() != null){
      throw new RuntimeException("OracleHierarchicalExpression is not supported");
    }
    if(plainSelect.getOrderByElements() != null){
      throw new RuntimeException("ORDER BY is not supported");
    }
    if(plainSelect.getTop() != null){
      throw new RuntimeException("TOP is not supported");
    }

    if(plainSelect.getGroupByColumnReferences() != null){
      stage = Constants.ValidateStage.GROUPBY;
      for(Expression groupby: plainSelect.getGroupByColumnReferences()){
        groupby.accept(this);
      }
    }else if(multipleTopic){
      throw new RuntimeException("Select from multiple topics must be inside a window");
    }

    if(plainSelect.getSelectItems() != null){
      stage = Constants.ValidateStage.SELECT;
      for (SelectItem selectItem : plainSelect.getSelectItems()) {
        selectItem.accept(this);
      }
    }else{
      throw new RuntimeException("SELECT item is required");
    }

    if(plainSelect.getFromItem() != null){
      stage = Constants.ValidateStage.FROM;
      plainSelect.getFromItem().accept(this);
    }

    if (plainSelect.getJoins() != null) {
      stage = Constants.ValidateStage.JOIN;
      for (Join join : plainSelect.getJoins()) {
        join.getRightItem().accept(this);
      }
    }
    if (plainSelect.getWhere() != null) {
      stage = Constants.ValidateStage.WHERE;
      plainSelect.getWhere().accept(this);
    }

    if(plainSelect.getHaving() != null){
      stage = Constants.ValidateStage.HAVING;
      plainSelect.getHaving().accept(this);
    }
  }

  @Override
  public void visit(SetOperationList setOpList) {
    throw new RuntimeException(String.format("SetOperationList %s is not supported", setOpList));
  }

  @Override
  public void visit(WithItem withItem) {
    throw new RuntimeException("With is not supported");
  }

  @Override
  public void visit(AllColumns allColumns) {

  }

  @Override
  public void visit(AllTableColumns allTableColumns) {

  }

  @Override
  public void visit(SelectExpressionItem selectExpressionItem) {
    selectExpressionItem.getExpression().accept(this);
  }
}
