package io.emqx.stream.common.sql.visitor;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlExecutionContext;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import net.sf.jsqlparser.expression.Expression;
import org.slf4j.Logger;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RequiredArgsConstructor
public class ExpressionFilter {
  private final @NonNull
  Logger logger;

  public List<Map<String, Object>> filterWhere(Expression filterExp, SqlExecutionContext context) {
    List<Map<String, Object>> records = context.joins() != null ? context.joins() : context.records();
    //TODO optimize here if needed
    records.forEach(record -> {
      if (!record.containsKey(Constants.CONDITION)) {
        boolean condition = (boolean) new ExpressionEvaluator().evaluate(filterExp, record, context);
        record.put(Constants.CONDITION, condition);
      }
    });
    return records;
  }

  public List<Map<String, Object>> filterHavingNoGroup(Expression filterExp, SqlExecutionContext context) {
    List<Map<String, Object>> records = context.records();
    //If there is having on outer group, distinct the pass state of where and having
    records.forEach(record -> {
      if (!record.containsKey(Constants.PASSWHERE)) {
        boolean whereState = (boolean) record.getOrDefault(Constants.CONDITION, true);
        record.put(Constants.PASSWHERE, whereState);
      }
    });
    boolean havingState = (boolean) new ExpressionEvaluator().evaluate(filterExp, records.size() > 0 ? records.get(0) : null, context);
    records.forEach(record -> {
      boolean whereState = (boolean) record.getOrDefault(Constants.PASSWHERE, true);
      record.put(Constants.CONDITION, whereState && havingState);
    });
    //If having size == 0
    if(records.size() == 0 && havingState){
      records.add(new HashMap<>());
    }
    return records;
  }

  public Map<String, List<Map<String, Object>>> filterHaving(Expression filterExp, SqlExecutionContext context) {
    return context.groups().entrySet().parallelStream()
            .filter(map -> {
              List<Map<String, Object>> newList = map.getValue().parallelStream().filter(record -> {
                //TODO optimize aggregate result
                boolean havingResult = (boolean) new ExpressionEvaluator().evaluate(filterExp, record, context);
                record.put(Constants.HAVING, havingResult);
                return havingResult;
              }).collect(Collectors.toList());
              map.setValue(newList);
              return !newList.isEmpty();
            })
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
  }
}