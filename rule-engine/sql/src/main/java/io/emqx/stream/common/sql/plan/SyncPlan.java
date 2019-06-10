package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.SqlExecutionContext;
import io.emqx.stream.common.sql.pojo.Window;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static io.emqx.stream.common.Constants.WindowType.*;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true) @Data
public class SyncPlan extends PlanAdaptor {
  private Window window;

  @Override
  public SqlExecutionContext execute(SqlExecutionContext context) throws Exception {
    context = super.execute(context);
    sync(context);
    context.resetIntermediates();
    return context;
  }

  private void sync(SqlExecutionContext context) {
    if(context.lastRecords() == null){
      return;
    }
    // Sync record if current record existing
    if(window != null && !window.type().equals(TUMBLING)){
      switch(window.type()){
        case TUMBLING:
        case SESSION:
          break;
        case HOPPING:
          syncHoppingWindow(context);
          break;
        case SLIDING:
          //Only one record each time
          syncSlidingWindow(context);
          break;
      }
    }
  }

  private void syncSlidingWindow(SqlExecutionContext context) {
    long size = window.size();
    List<Map<String, Object>> records = context.records();
    List<Map<String, Object>> lastRecords = context.lastRecords();

    long currentTs = (long) records.get(0).get(Constants.MESSAGE_TIMESTAMP);
    int length = lastRecords.size();
    int skipLength;
    if(window.isDuration()){
      for(skipLength=0;skipLength<length;skipLength++){
        if(currentTs - (long)lastRecords.get(skipLength).get(Constants.MESSAGE_ID_FIELD) <= size ){
          break;
        }
      }
    }else{
      skipLength = 1;
    }
    context.records(Stream.concat(lastRecords.stream().skip(skipLength), records.stream())
            .collect(Collectors.toList()));
    context.lastRecords(lastRecords.subList(0, skipLength));
  }

  private void syncHoppingWindow(SqlExecutionContext context) {
    List<Map<String, Object>> records = context.records();
    List<Map<String, Object>> lastRecords = context.lastRecords();
    int validIndex;
    int length = lastRecords.size();
    long ts = (long) records.get(0).get(Constants.MESSAGE_ID_FIELD);
    //TODO message ID?
    for(validIndex=0;validIndex<length;validIndex++){
      if((long)lastRecords.get(0).get(Constants.MESSAGE_ID_FIELD) == ts){
        break;
      }
    }
    context.records(Stream.concat(lastRecords.stream().skip(validIndex), records.stream().skip(length - validIndex))
            .collect(Collectors.toList()));
    context.lastRecords(lastRecords.subList(0, validIndex));
  }
}
