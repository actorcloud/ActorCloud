package io.emqx.stream.common.sql.analyzer;

import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.select.*;

import java.util.List;

@RequiredArgsConstructor
public class FromItemAnalyzer implements FromItemVisitor {
  @NonNull
  private final List<FromItem> fromItems;

  @Override
  public void visit(Table table) {
    fromItems.add(table);
  }

  @Override
  public void visit(SubSelect subSelect) {
    fromItems.add(subSelect);
  }

  @Override
  public void visit(SubJoin subJoin) {

  }

  @Override
  public void visit(LateralSubSelect lateralSubSelect) {
    //Only deal in join
  }

  @Override
  public void visit(ValuesList valuesList) {
    fromItems.add(valuesList);
  }
}
