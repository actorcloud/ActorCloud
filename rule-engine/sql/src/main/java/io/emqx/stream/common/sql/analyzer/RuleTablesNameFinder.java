package io.emqx.stream.common.sql.analyzer;

import net.sf.jsqlparser.statement.select.Join;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.util.TablesNamesFinder;

public class RuleTablesNameFinder extends TablesNamesFinder {
  @Override
  public void visit(PlainSelect plainSelect) {
    if(plainSelect.getFromItem()!= null){
      plainSelect.getFromItem().accept(this);
    }

    if (plainSelect.getJoins() != null) {
      for (Join join : plainSelect.getJoins()) {
        join.getRightItem().accept(this);
      }
    }
    if (plainSelect.getWhere() != null) {
      plainSelect.getWhere().accept(this);
    }

  }
}
