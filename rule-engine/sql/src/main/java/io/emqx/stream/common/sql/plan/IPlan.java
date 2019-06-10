package io.emqx.stream.common.sql.plan;

import io.emqx.stream.common.sql.SqlExecutionContext;

public interface IPlan{
  @SuppressWarnings("UnusedReturnValue")
  IPlan dependant(IPlan dependant);
  //Return a list of hashMap or a hashMap of list of hashMap
  SqlExecutionContext execute(SqlExecutionContext context) throws Exception;
}