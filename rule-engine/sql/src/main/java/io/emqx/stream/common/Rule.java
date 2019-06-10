package io.emqx.stream.common;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import org.slf4j.Logger;

import io.emqx.stream.common.sql.ISqlEngine;
import io.emqx.stream.common.sql.SqlEngine;

import lombok.Getter;
import net.sf.jsqlparser.JSQLParserException;

public class Rule implements IRule {
  private ISqlEngine engine;
  @Getter
  private List<Map<String, Object>> actions;
  // --Commented out by Inspection (2019/4/10 0010 上午 10:30):private CompletableFuture<Void> processFuture;

  public Rule(String rawStr, Logger logger) throws JSQLParserException {
    this(Objects.requireNonNull(JsonParser.parseRule(rawStr)), logger);
  }

  @SuppressWarnings({"unchecked", "WeakerAccess"})
  public Rule(Map<String, Object> payload, Logger logger) throws JSQLParserException {
    String sql = (String) payload.get("sql");
    engine = new SqlEngine(sql, logger);
    actions = (List<Map<String, Object>>) payload.get("actions");
  }

  @Override
  public List<Map<String, Object>> apply(List<Map<String,Object>> messages) throws Exception {
    return engine.process(messages);
  }

}