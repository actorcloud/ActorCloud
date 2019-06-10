package io.emqx.stream.common.sql;

import lombok.Data;
import lombok.experimental.Accessors;
import org.slf4j.Logger;

import java.util.List;
import java.util.Map;

@Accessors(fluent = true) @Data
public class SqlExecutionContext {

  Logger logger;

  /**
   * The original record list.
   * The existing element fields won't be changed during execution,
   * but the element will add "mark" field like "__group" to store the state
   * during execution. And it will be used to skip further process if the state
   * is already in place.
   */
  List<Map<String, Object>> records;

  /**
   * The last processed record list with marked fields
   */
  List<Map<String, Object>> lastRecords;

  /**
   * Created when there is grouping.
   * The key will be the group item value.
   * The value will be the records that is in the group.
   */
  Map<String, List<Map<String, Object>>> groups;

  /**
   * Created when there is multiple from(topic).
   * The records will be separated into hashMap
   */
  Map<String, List<Map<String, Object>>> topics;

  /**
   * Created when there is join statement.
   * The records will be uses as a replacement for records
   */
  List<Map<String, Object>> joins;

  /**
   * The final output
   */
  List<Map<String, Object>> results;

  /**
   * The joined row when running lateral join
   */
  Map<String, Object> lateralRow;

  public void resetIntermediates() {
    groups = null;
    topics = null;
    joins = null;
    results = null;
  }
}
