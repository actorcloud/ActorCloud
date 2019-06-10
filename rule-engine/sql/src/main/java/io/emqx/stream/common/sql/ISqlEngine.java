package io.emqx.stream.common.sql;

import java.util.List;
import java.util.Map;

public interface ISqlEngine {
  List<Map<String, Object>> process(Map<String, Object> message) throws Exception;
  List<Map<String,Object>> process(List<Map<String, Object>> message) throws Exception;
}