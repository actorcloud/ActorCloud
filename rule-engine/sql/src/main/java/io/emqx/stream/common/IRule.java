package io.emqx.stream.common;

import java.util.List;
import java.util.Map;

public interface IRule {
  /**
   * Run the rule against the new message. The input
   * is the current message.The state(window) needs to 
   * be stored by the rule processor.
   */
  List<Map<String, Object>> apply(List<Map<String,Object>> inputs) throws Exception;
  List<Map<String, Object>> getActions();
}