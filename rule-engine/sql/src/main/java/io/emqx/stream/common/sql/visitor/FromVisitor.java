package io.emqx.stream.common.sql.visitor;

import io.emqx.stream.common.sql.SqlEngine;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.select.*;
import org.slf4j.Logger;

import java.util.List;
import java.util.Map;

@RequiredArgsConstructor
public class FromVisitor implements FromItemVisitor {
  @NonNull
  private final Logger logger;
  private List<Map<String, Object>> records;
  private Map<String, List<Map<String, Object>>> topics;

  public List<Map<String, Object>> apply(FromItem fromItem, List<Map<String, Object>> inputRecords, Map<String, List<Map<String, Object>>> topics){
    records = inputRecords;
    this.topics = topics;
    fromItem.accept(this);
    return records;
  }

  @Override
  public void visit(Table table) {
    if(topics != null && table.getAlias() != null){
      topics.put(table.getAlias().getName(), topics.remove(table.getName()));
    }
  }

  @Override
  public void visit(SubSelect subSelect) {
    SqlEngine subEngine = new SqlEngine(subSelect.getSelectBody(), logger);
    try {
      records = subEngine.process(records);
      if(topics != null){
        String name = subSelect.getAlias() != null ? subSelect.getAlias().getName() : subSelect.toString();
        topics.put(name, records);
      }
    } catch (Exception e) {
      // TODO Auto-generated catch block
    }
  }

  @Override
  public void visit(SubJoin subJoin) {

  }

  @Override
  public void visit(LateralSubSelect lateralSubSelect) {


  }

  @Override
  public void visit(ValuesList valuesList) {

  }
}
