package io.emqx.stream.common.sql.analyzer;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.Util;
import io.emqx.stream.common.sql.plan.JoinPlan;
import io.emqx.stream.common.sql.pojo.JoinCondition;
import io.emqx.stream.common.sql.pojo.Tuple;
import lombok.Getter;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.expression.*;
import net.sf.jsqlparser.expression.operators.conditional.AndExpression;
import net.sf.jsqlparser.expression.operators.relational.*;
import net.sf.jsqlparser.schema.Column;
import net.sf.jsqlparser.statement.select.FromItem;
import net.sf.jsqlparser.statement.select.LateralSubSelect;

import java.util.LinkedList;
import java.util.Map;

@RequiredArgsConstructor
public class JoinConditionAnalyzer extends ExpressionVisitorAdapter {
  @NonNull
  private final JoinPlan joinPlan;
  @NonNull
  private Constants.JoinType joinType;

  /**
   * The modified condition expression that has removed all equivalent criteria
   */
  @Accessors(fluent = true) @Getter
  private Expression parent;

  private Column leftColumn;
  private Column rightColumn;
  private boolean isOn;

  private void addExpression(Expression expr){
    if(expr != null){
      if(parent == null || parent instanceof NullValue){
        parent = expr;
      }else{
        parent = new AndExpression(parent, expr);
      }
    }
  }

  private void modifyParent(Expression expr) {
    if(isOn){
      if(parent == null){
        parent = new NullValue();
      }
    }else{
      addExpression(expr);
    }
  }

  @Override
  public void visit(AndExpression expr){
    expr.getLeftExpression().accept(this);
    needModifyParent(expr.getLeftExpression());
    expr.getRightExpression().accept(this);
    needModifyParent(expr.getRightExpression());
  }

  private void needModifyParent(Expression expr) {
    if(!isOn){
      modifyParent(expr);
    }else{
      isOn=false;
    }
  }

  @Override
  public void visit(Parenthesis parenthesis) {
    parenthesis.getExpression().accept(this);
  }

  @Override
  public void visit(EqualsTo expr) {
    expr.getLeftExpression().accept(this);
    if(leftColumn != null){
      expr.getRightExpression().accept(this);
      if(rightColumn != null){
        isOn = true;
        addJoinCondition();
        rightColumn = null;
      }
      leftColumn = null;
    }
    modifyParent(expr);
  }

  public void addJoinCondition(FromItem rightTopic){
    String rightTopicName = Util.getFromItemName(rightTopic);
    JoinCondition joinCondition = joinPlan.joinConditions().get(rightTopicName);
    if(joinCondition == null){
      joinCondition = new JoinCondition().equivalents(new LinkedList<>()).type(joinType);
      if(rightTopic instanceof LateralSubSelect){
        joinCondition.lateral(((LateralSubSelect) rightTopic).getSubSelect());
      }
      joinPlan.joinConditions().put(rightTopicName, joinCondition);
    }
  }

  //Join conditions are preserved the join order
  private void addJoinCondition() {
    String leftTableName = Util.getFromItemName(leftColumn.getTable());
    String rightTableName = Util.getFromItemName(rightColumn.getTable());
    String rightTopic = rightTableName;
    boolean switchLeftRight = false;
    //noinspection StatementWithEmptyBody
    if(leftTableName.equalsIgnoreCase(joinPlan.fromName())){
      //do nothing, keep default value
    } else if (rightTableName.equalsIgnoreCase(joinPlan.fromName())) {
      rightTopic = leftTableName;
      switchLeftRight = true;
    }else{
      //Check which topic occurs earlier
      for(Map.Entry<String, JoinCondition> entry:joinPlan.joinConditions().entrySet()){
        if(entry.getKey().equalsIgnoreCase(leftTableName)){
          break;
        }else if(entry.getKey().equalsIgnoreCase(rightTableName)){
          rightTopic = leftTableName;
          switchLeftRight = true;
          break;
        }
      }
    }
    JoinCondition joinCondition = joinPlan.joinConditions().get(rightTopic);
    Tuple<String, String> value = switchLeftRight ? new Tuple<>(rightTableName + "." + rightColumn.getColumnName(), leftColumn.getColumnName()) : new Tuple<>(leftTableName + "." + leftColumn.getColumnName(), rightColumn.getColumnName());
    joinCondition.equivalents().add(value);
  }

  // Assume only possible to be an expression of EqualsTo
  @Override
  public void visit(Column column) {
    if(leftColumn == null){
      leftColumn = column;
    }else{
      rightColumn = column;
    }
  }

  // Override to clean up the parent class behavior
  @Override
  protected void visitBinaryExpression(BinaryExpression expr) {
    //do nothing
  }

  @Override
  public void visit(Between expr) {
    //do nothing
  }

  @Override
  public void visit(InExpression expr) {
    //do nothing
  }

  @Override
  public void visit(IsNullExpression expr) {
    //do nothing
  }

  @Override
  public void visit(CaseExpression expr) {
    //do nothing
  }

  @Override
  public void visit(WhenClause expr) {
    //do nothing
  }

  @Override
  public void visit(ExistsExpression expr) {
    //do nothing
  }

  @Override
  public void visit(CastExpression expr) {
    //do nothing
  }

  @Override
  public void visit(AnalyticExpression expr) {
    //do nothing
  }

  @Override
  public void visit(ExtractExpression expr) {
    //do nothing
  }

  @Override
  public void visit(OracleHierarchicalExpression expr) {
    //do nothing
  }

  @Override
  public void visit(ExpressionList expressionList) {
    //do nothing
  }

  @Override
  public void visit(MultiExpressionList multiExprList) {
    //do nothing
  }
}
