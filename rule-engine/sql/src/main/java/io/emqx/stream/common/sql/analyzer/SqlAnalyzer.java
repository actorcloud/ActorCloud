package io.emqx.stream.common.sql.analyzer;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.Util;
import io.emqx.stream.common.sql.plan.*;
import io.emqx.stream.common.sql.pojo.Selection;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.NullValue;
import net.sf.jsqlparser.statement.select.*;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;

/**
 * Return the static part of the query like output column, and window settings
 * The only entry point is process function
 */
@RequiredArgsConstructor
public class SqlAnalyzer implements SelectVisitor, SelectItemVisitor {

  private IPlan currentPlan;

  //For select item visitor
  private final OutputPlan outputPlan = new OutputPlan();
  private List<Selection> selectCols;

  private final @NonNull SelectBody statement;

  public IPlan process() {
    // initialization
    IPlan allPlan = new SqlPlan();
    currentPlan = allPlan;

    //features = new SqlFeatures();
    selectCols = new ArrayList<>();
    // do process
    statement.accept(this);

    return allPlan;
  }

  // *** SelectVisitor below **/
  @Override
  public void visit(PlainSelect plainSelect) {
    for (SelectItem selectItem : plainSelect.getSelectItems()) {
      selectItem.accept(this);
    }
    outputPlan.selectCols(selectCols);
    linkPlan(outputPlan);

    if (plainSelect.getHaving() != null) {
      FilterPlan havingPlan = new FilterPlan().isHaving(true);
      havingPlan.expression(plainSelect.getHaving());
      linkPlan(havingPlan);
    }

    List<Expression> groups = plainSelect.getGroupByColumnReferences();
    SyncPlan syncPlan = new SyncPlan();
    if(groups != null) {
      //TODO window and group distinguish
      AggregatePlan aggregatePlan = new AggregatePlan();
      Iterator<Expression> iterator = groups.iterator();
      //Pass iterator to analyzer in case it need to remove element
      GroupExpressionAnalyzer analyzer = new GroupExpressionAnalyzer(aggregatePlan, iterator);
      aggregatePlan.expressions(groups);
      while(iterator.hasNext()) {
        Expression group = iterator.next();
        group.accept(analyzer);
      }
      if(aggregatePlan.window() != null){
        syncPlan.window(aggregatePlan.window());
      }
      linkPlan(aggregatePlan);
    }

    ProjectPlan projectPlan = null;
    if (plainSelect.getFromItem() != null) {
      projectPlan = new ProjectPlan().fromItems(new ArrayList<>());
      FromItemAnalyzer fromItemAnalyzer = new FromItemAnalyzer(projectPlan.fromItems());
      //Create projectPlan inside
      plainSelect.getFromItem().accept(fromItemAnalyzer);
      outputPlan.hasFrom(true);
    }else{
      outputPlan.hasFrom(false);
    }

    JoinPlan joinPlan = null;
    FilterPlan wherePlan = new FilterPlan();
    if (plainSelect.getJoins() != null){
      FromItemAnalyzer fromItemAnalyzer = new FromItemAnalyzer(Objects.requireNonNull(projectPlan).fromItems());
      List<Join> joins = plainSelect.getJoins();
      joinPlan = new JoinPlan();
      joinPlan.fromName(Util.getFromItemName(plainSelect.getFromItem()));

      for(Join join: joins){
        join.getRightItem().accept(fromItemAnalyzer);
        AnalyzeFilter(joinPlan, wherePlan, join.getRightItem(), join.getOnExpression(), getJoinType(join));
      }
    }

    if (plainSelect.getWhere() != null) {
      //TODO join type may not be simple
      AnalyzeFilter(joinPlan, wherePlan, null, plainSelect.getWhere(), Constants.JoinType.SIMPLE);
    }

    if(wherePlan.expression() != null){
      linkPlan(wherePlan);
    }

    if(joinPlan != null){
      linkPlan(joinPlan);
    }

    if(projectPlan != null){
      linkPlan(projectPlan);
    }

    linkPlan(syncPlan);
  }

  private Constants.JoinType getJoinType(Join join) {
    if(join.isSimple()){
      return Constants.JoinType.SIMPLE;
    }else if(join.isInner()){
      return Constants.JoinType.INNER;
    }else if(join.isOuter()){
      return Constants.JoinType.OUTER;
    }else if(join.isLeft()){
      return Constants.JoinType.LEFT;
    }else if(join.isRight()){
      return Constants.JoinType.RIGHT;
    }else{
      return Constants.JoinType.SIMPLE;
    }
  }

  private void AnalyzeFilter(JoinPlan joinPlan, FilterPlan wherePlan, FromItem rightItem, Expression filterExpression, Constants.JoinType joinType) {
    if(joinPlan != null){
      JoinConditionAnalyzer joinAnalyzer = new JoinConditionAnalyzer(joinPlan, joinType);
      if(rightItem != null){
        joinAnalyzer.addJoinCondition(rightItem);
      }
      if(filterExpression != null){
        filterExpression.accept(joinAnalyzer);
        if (joinAnalyzer.parent() != null) {
          if(!(joinAnalyzer.parent() instanceof NullValue)){
            wherePlan.addCondition(joinAnalyzer.parent());
          }
        }else{
          wherePlan.addCondition(filterExpression);
        }
      }
    }
    else{
      wherePlan.addCondition(filterExpression);
    }
  }

  private void linkPlan(IPlan plan) {
    currentPlan.dependant(plan);
    currentPlan = plan;
  }

  @Override
  public void visit(SetOperationList setOpList) {
    // do nothing for now
  }

  @Override
  public void visit(WithItem withItem) {
    throw new RuntimeException("with is not supported");
  }

  @Override
  public void visit(AllColumns allColumns) {
    Selection selection = new Selection();
    selection.all(true);
    this.selectCols.add(selection);
  }

  @Override
  public void visit(AllTableColumns allTableColumns) {
    Selection selection = new Selection();
    selection.all(true);
    selection.table(allTableColumns.getTable());
    this.selectCols.add(selection);
  }

  // *** SelectItemVisitor below **/
  @Override
  public void visit(SelectExpressionItem selectExpressionItem) {
    Selection selection = new Selection();
    SelectExpressionAnalyzer analyzer = new SelectExpressionAnalyzer(selection);
    selectExpressionItem.getExpression().accept(analyzer);
    if(selection.expression() == null){
      selection.expression(selectExpressionItem.getExpression()).outputName(selectExpressionItem.getExpression().toString());
    }
    // TODO other alias properties?
    if (selectExpressionItem.getAlias() != null) {
      selection.outputName(selectExpressionItem.getAlias().getName());
    }
    this.selectCols.add(selection);  
  }
}