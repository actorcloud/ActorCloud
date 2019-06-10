package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlEngine;
import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.Util;
import io.emqx.stream.common.sql.pojo.JoinCondition;
import io.emqx.stream.common.sql.pojo.Tuple;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.statement.select.SubSelect;

import java.util.*;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class JoinPlan extends PlanAdaptor {

  private String fromName;
  /**
   * The analyzed join conditions
   * The value is a list of column tuples to indicate the equal criteria
   * The value is ordered by the order in the from clause
   */
  private Map<String, JoinCondition> joinConditions = new LinkedHashMap<>();

  /**
   *  Input: topics
   *  Output: joins
   */
  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    context = super.execute(context);
    Map<String, List<Map<String, Object>>> topics = context.topics();
    //Hash merge
    SqlExecutionContext finalContext = context;
    for (Map.Entry<String, JoinCondition> entry : joinConditions.entrySet()) {
      String key = entry.getKey();
      JoinCondition condition = entry.getValue();
      boolean isLateral = condition.lateral() != null;
      String buildTableName = fromName;
      List<Map<String, Object>> buildTable;
      List<Map<String, Object>> probeTable = null;
      if (topics != null && !topics.isEmpty()) {
        buildTable = topics.getOrDefault(buildTableName, finalContext.joins());
        probeTable = topics.getOrDefault(key, finalContext.joins());
      } else if (isLateral) {
        buildTable = finalContext.joins() != null ? finalContext.joins() : finalContext.records();
      } else {
        throw new RuntimeException(String.format("Cannot find table %s for join", key));
      }

      List<Map<String, Object>> results = new LinkedList<>();
      boolean hasEquivalent = condition.equivalents().size() > 0;
      if (hasEquivalent) { //do hash join
        Map<String, List<Map<String, Object>>> topic2Hash = null;
        if (!isLateral) {
          topic2Hash = new HashMap<>();
          createHashTable(condition, probeTable, topic2Hash);
        }
        for (Map<String, Object> record : buildTable) {
          Map<String, Object> result;
          if((boolean)record.getOrDefault(Constants.JOIN_FIELD, false)) {
            result = new HashMap<>(record);
          }else{
            result = new HashMap<>();
          }
          if (isLateral) {
            topic2Hash = new HashMap<>();
            probeTable = createLateralTable(condition, finalContext, record);
            createHashTable(condition, probeTable, topic2Hash);
          }
          String hashKey = getHash(condition, record);
          List<Map<String, Object>> topic2Records = topic2Hash.get(hashKey);
          if (topic2Records == null || topic2Records.isEmpty()) {
            if (condition.type() == Constants.JoinType.LEFT || condition.type() == Constants.JoinType.OUTER) {
              result.put(buildTableName, record);
              result.put(Constants.JOIN_FIELD, true);
              results.add(result);
            }
          } else {
            for (Map<String, Object> record2 : topic2Hash.getOrDefault(hashKey, new LinkedList<>())) {
              result.putIfAbsent(buildTableName, record);
              result.put(key, record2);
              result.put(Constants.JOIN_FIELD, true);
              results.add(result);
              result = new HashMap<>();
            }
          }
        }
        //TODO lateral outer join
        if (!isLateral && (condition.type() == Constants.JoinType.OUTER || condition.type() == Constants.JoinType.RIGHT)
                && !topic2Hash.isEmpty()) {
          Map<String, Object> result = new HashMap<>();
          for (List<Map<String, Object>> records : topic2Hash.values()) {
            for (Map<String, Object> record : records) {
              result.put(key, record);
              result.put(Constants.JOIN_FIELD, true);
              results.add(result);
              result = new HashMap<>();
            }
          }
        }
      } else { //If no condition, double loop through all
        for (Map<String, Object> leftRecord : buildTable) {
          if (isLateral) {
            probeTable = createLateralTable(condition, finalContext, leftRecord);
          }
          for (Map<String, Object> rightRecord : probeTable) {
            Map<String, Object> result;
            if((boolean)leftRecord.getOrDefault(Constants.JOIN_FIELD, false)){
              result = new HashMap<>(leftRecord);
            }else{
              result = new HashMap<>();
              result.putIfAbsent(buildTableName, leftRecord);
            }
            result.put(key, rightRecord);
            result.put(Constants.JOIN_FIELD, true);
            results.add(result);
          }
        }
      }
      finalContext.joins(results);
      if (topics != null && !topics.isEmpty()) {
        topics.remove(buildTableName);
        topics.remove(key);
      }
    }
    return context;
  }

  private List<Map<String, Object>> createLateralTable(JoinCondition condition, SqlExecutionContext context, Map<String, Object> row) throws Exception {
    SubSelect subSelect = condition.lateral();
    SqlEngine subEngine = new SqlEngine(subSelect.getSelectBody(), context.logger());
    List<Map<String, Object>> probeTable;
    //Because the join is merging topics from left to right during which the merged topics are removed from topics
    //That means in the lateral, the "left" topics are already defined at the merged row;And the right topics are still
    //inside topics
    if(!(boolean)row.getOrDefault(Constants.JOIN_FIELD, false)){
      Map<String, Object> newRow = new HashMap<>();
      newRow.put(fromName, row);
      probeTable = subEngine.process(Util.deepCopyMapList(context.records()), newRow);
    }else{
      probeTable = subEngine.process(Util.deepCopyMapList(context.records()), row);
    }
    return probeTable;
  }

  private void createHashTable(JoinCondition condition, List<Map<String, Object>> probeTable, Map<String, List<Map<String, Object>>> topic2Hash) {
    probeTable.forEach(rec -> {
      String hashKey = getHash(condition, rec);
      topic2Hash.putIfAbsent(hashKey, new LinkedList<>());
      topic2Hash.get(hashKey).add(rec);
    });
  }

  @SuppressWarnings("unchecked")
  private String getHash(JoinCondition condition, Map<String, Object> rec) {
    StringBuilder hashKey = new StringBuilder();
    boolean isJoined = (boolean) rec.getOrDefault(Constants.JOIN_FIELD, false);
    for(Tuple<String, String> tuple: condition.equivalents()){
      Map<String,Object> currentTable = rec;
      String col = tuple.left();
      String[] parts = col.split("\\.");
      if(parts.length == 2){
        if(isJoined){
          currentTable = (Map<String, Object>) rec.get(parts[0]);
        }
        col = parts[1];
      }
      hashKey.append(",").append(currentTable.get(col).toString());
    }
    return hashKey.toString();
  }
}
