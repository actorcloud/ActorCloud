package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.Util;
import io.emqx.stream.common.sql.pojo.Selection;
import io.emqx.stream.common.sql.visitor.ExpressionEvaluator;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.schema.Table;

import java.util.*;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class OutputPlan extends PlanAdaptor{
  private List<Selection> selectCols;
  private boolean hasFrom;

  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    List<Map<String, Object>> results = new ArrayList<>();
    context = super.execute(context);
    if(context.groups() != null){
      for(List<Map<String, Object>> group: context.groups().values()){
        handleGroupOutput(group, results, context);
      }
    }else if(hasFrom){
      //If running join, then the latest result is in join
      List<Map<String, Object>> outputs = context.joins() != null ? context.joins() : context.records();
      for (Map<String, Object> record : outputs) {
        handleRecordOutput(record, results, context);
      }
    }else if(context.lateralRow() != null){
      handleRecordOutput(context.lateralRow(), results, context);
    }
    context.results(results);
    return context;
  }

  private void handleGroupOutput(List<Map<String, Object>> group, List<Map<String, Object>> results, SqlExecutionContext context) {
    final Map<String, Object> record = group.get(0);
    //TODO aggregate functions
    handleRecordOutput(record, results, context);
  }

  private void handleRecordOutput(Map<String, Object> record, List<Map<String, Object>> results, SqlExecutionContext context) {
    final Map<String, Object> resultMap;
    if ((boolean) record.getOrDefault(Constants.CONDITION, true)) {
      resultMap = new HashMap<>();
      ExpressionEvaluator evaluator = new ExpressionEvaluator();
      List<String> unnests = new LinkedList<>();
      for (Selection col : selectCols) {
        if (col.all()) {
          if (col.table() == null) {
            flat(record).forEach((key, value) -> {
              if (!key.startsWith(Constants.PRIVATE_FIELD_SIGN)) {
                resultMap.put(key, value);
              }
            });
          } else {
            Table table = col.table();
            String tableName = Util.getFromItemName(table);
            Map<String, Object> flatRecord;
            if ((boolean) record.getOrDefault(Constants.JOIN_FIELD, false)) {
              //noinspection unchecked
              flatRecord = (Map<String, Object>) record.get(tableName);
            } else {
              flatRecord = record;
            }
            flatRecord.forEach((key, value) -> {
              if (!key.startsWith(Constants.PRIVATE_FIELD_SIGN)) {
                resultMap.put(tableName + "." + key, value);
              }
            });
          }
        }else{
          String resultName = col.outputName();
          String[] resultNames = resultName.split(Constants.RECORD_FIELD_SEPERATOR);
          Object colValue = evaluator.evaluate(col.expression(), record, context);

          Object parentResult;
          Object subResult = resultMap;
          for(int i=0;i<resultNames.length;i++){
            String name = resultNames[i];
            parentResult = subResult;
            //noinspection unchecked
            subResult = ((Map<String, Object>) Objects.requireNonNull(parentResult)).get(name);
            if(subResult == null && i<resultNames.length - 1){
              subResult = new HashMap<String, Object>();
            }
            if(i==resultNames.length - 1){
              subResult = colValue;
            }
            //noinspection unchecked
            ((Map<String, Object>)parentResult).put(name, subResult);
          }
          if(col.unnest() > 0){
            //If cross apply, the empty array won't go to the next flat process
            if(col.unnest() == Constants.CROSS_APPLY ){
              Object nestObj = resultMap.get(resultNames[0]);
              if(nestObj instanceof List){
                if(((List) nestObj).size() == 0){
                  return;
                }
              }else{
                throw new RuntimeException(String.format("Cannot run unnest function on non-array inputs: %s", nestObj));
              }
            }
            unnests.add(col.outputName());
          }
        }
      }
      if(unnests.size() > 0){
        List<Map<String, Object>> unnestResults = new LinkedList<>();
        //Flatting
        for(String unnest:unnests){
          List array = (List) resultMap.get(unnest);
          resultMap.remove(unnest);
          List<Map<String, Object>> newResults = new LinkedList<>();
          if(array.size() > 0){
            for(Object value: array){
              if(unnestResults.size() > 0){
                for(Map<String, Object> uResult: unnestResults){
                  Map<String, Object> newRow = new HashMap<>(uResult);
                  newRow.put(unnest, value);
                  newResults.add(newRow);
                }
              }else{
                Map<String, Object> newRow = new HashMap<>();
                newRow.put(unnest, value);
                newResults.add(newRow);
              }
            }
          }else{
            Map<String, Object> newRow = new HashMap<>();
            newRow.put(unnest, null);
            newResults.add(newRow);
          }
          unnestResults = newResults;
        }
        if(unnestResults.size() > 0){
          for(Map<String, Object> uResult: unnestResults){
            Map<String, Object> combinedResult = new HashMap<>();
            combinedResult.putAll(resultMap);
            combinedResult.putAll(uResult);
            results.add(combinedResult);
          }
        }else{ //Outer apply
          results.add(resultMap);
        }
      }else{
        results.add(resultMap);
      }
    }
  }

  private Map<String, Object> flat(Map<String, Object> record) {
    Map<String, Object> flatRecord;
    if((boolean)record.getOrDefault(Constants.JOIN_FIELD, false)){
      flatRecord = new HashMap<>();
      record.forEach((table, rec) -> {
        if(!table.startsWith(Constants.PRIVATE_FIELD_SIGN)){
          //noinspection unchecked
          Map<String, Object> subRecord = (Map<String, Object>) rec;
          subRecord.forEach((col, value)-> flatRecord.put(table + "." + col,value ));
        }
      });
    }else{
      flatRecord = record;
    }
    return flatRecord;
  }
}