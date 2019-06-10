package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.visitor.FromVisitor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;
import net.sf.jsqlparser.statement.select.FromItem;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

/**
 * Populate the subQuery
 */
@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class ProjectPlan extends PlanAdaptor {
  private List<FromItem> fromItems = new LinkedList<>();

  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    context = super.execute(context);
    FromVisitor fromVisitor = new FromVisitor(context.logger());
    if(fromItems.size() > 1){
      //hashing with topic name
      Map<String, List<Map<String, Object>>> topics = new HashMap<>();
      context.records().forEach(record -> {
        String topicName = (String) record.get(Constants.TOPIC_FIELD);
        if(topics.containsKey(topicName)){
          topics.get(topicName).add(record);
        }else{
          topics.put(topicName, new LinkedList<Map<String, Object>>(){{add(record);}});
        }
      });
      for(FromItem fromItem: fromItems){
        fromVisitor.apply(fromItem, context.records(), topics);
      }
      context.topics(topics);
    }else if(fromItems.size() == 1){
      context.records(fromVisitor.apply(fromItems.get(0), context.records(), null));
    }
    return context;
  }
}