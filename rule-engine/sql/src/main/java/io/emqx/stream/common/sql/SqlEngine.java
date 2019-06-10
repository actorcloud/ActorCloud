package io.emqx.stream.common.sql;

import io.emqx.stream.common.sql.analyzer.SqlAnalyzer;
import io.emqx.stream.common.sql.plan.IPlan;
import net.sf.jsqlparser.JSQLParserException;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.select.Select;
import net.sf.jsqlparser.statement.select.SelectBody;
import org.slf4j.Logger;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * This class is stateful
 * It will save the record info according to the sql statement.
 */
public class SqlEngine implements ISqlEngine {
  //Immutable
  private Logger logger;
  private IPlan plan;
  private SqlExecutionContext context;
  // Queue of ts of the items that have fulfill condition in a session
//private Map<String, Object> lastMessage;
//private Queue<Long> sessionQueue;
//private long lastInvalidTs;

// --Commented out by Inspection START (2019/4/10 0010 上午 10:29):
//  public SqlEngine(Select select, Logger logger) {
//    init(select.getSelectBody(), logger);
//  }
// --Commented out by Inspection STOP (2019/4/10 0010 上午 10:29)

  public SqlEngine(SelectBody statement, Logger logger) {
    init(statement, logger);
  }
  
  public SqlEngine(String sql, Logger logger) throws JSQLParserException {
    init(((Select) CCJSqlParserUtil.parse(sql)).getSelectBody(), logger);
  }

  private void init(SelectBody statement, Logger logger){
    this.logger = logger;
    context = new SqlExecutionContext().logger(logger);
    plan = analyze(statement);
  }

  private IPlan analyze(SelectBody statement) {
    logger.info("analyze");
    SqlAnalyzer analyzer = new SqlAnalyzer(statement);
    return analyzer.process();
  }

  @Override
  public List<Map<String, Object>> process(Map<String, Object> message) throws Exception {
    return this.process(new ArrayList<>(Collections.singletonList(message)));
  }

  public List<Map<String, Object>> process(List<Map<String, Object>> records) throws Exception {
    //TODO more fine grained last record manipulation
    context.lastRecords(context.records()).records(records);
    context = plan.execute(context);
    return context.results();
  }

  public List<Map<String, Object>> process(List<Map<String, Object>> records, Map<String, Object> lateralRow) throws Exception {
    context.lateralRow(lateralRow);
    return this.process(records);
  }

}