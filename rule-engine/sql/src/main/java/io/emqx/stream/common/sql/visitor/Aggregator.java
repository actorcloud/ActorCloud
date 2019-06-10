package io.emqx.stream.common.sql.visitor;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlExecutionContext;
import net.sf.jsqlparser.expression.Expression;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Aggregator {
  private final ExpressionEvaluator evaluator = new ExpressionEvaluator();

  public Map<String, List<Map<String, Object>>> grouping(List<Expression> groupExpressions, SqlExecutionContext context) {
    List<Map<String, Object>> records = context.records();
    Map<String, List<Map<String, Object>>> groups = context.groups();
    if(groups == null) {
      groups = new HashMap<>();
    }
    Map<String, List<Map<String, Object>>> finalGroups = groups;
    records.forEach(record ->{
      if((boolean) record.getOrDefault(Constants.CONDITION, true)) {
        String key;
        if(record.get(Constants.GROUP) != null){
          key = (String) record.get(Constants.GROUP);
        }else{
          key = groupExpressions.parallelStream().map(exp ->
            (evaluator.evaluate(exp, record, context)).toString()
          ).reduce("", (x,y)->x+y);
        }        
        if(finalGroups.containsKey(key)){
          finalGroups.get(key).add(record);
        }else{
          List<Map<String, Object>> newGroup = new ArrayList<>();
          newGroup.add(record);
          finalGroups.put(key, newGroup);
        }
        record.put(Constants.GROUP, key);
      }
    });
    return groups;
  }
}