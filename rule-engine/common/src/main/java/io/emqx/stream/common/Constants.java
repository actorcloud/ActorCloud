package io.emqx.stream.common;
public final class Constants{

  public static final String MESSAGE_SEPERATOR = "%;";
  // Constants for marked field on the message
  public static final String CONDITION = "__condition";
  public static final String PASSWHERE = "__passWhere";
  public static final String GROUP = "__group";
  public static final String HAVING = "__having";

  public static final String MESSAGE_ID_FIELD = "__ts";
  public static final String MESSAGE_TIMESTAMP = "__ts";
  public static final String TOPIC_FIELD = "__topic";
  public static final String JOIN_FIELD = "__join";
  public static final String RECORD_FIELD_SEPERATOR = "\\$\\$";
  public static final int CROSS_APPLY = 1;
  public static final int OUTER_APPLY = 2;
  public static final String PRIVATE_FIELD_SIGN = "__";

  public static final String SESSION_CONFIG_KEY="__session";

  // Constants for window type
  public enum WindowType{
    TUMBLING,
    HOPPING,
    SLIDING,
    SESSION
  }

  public enum JoinType{
    SIMPLE,
    INNER,
    OUTER,
    LEFT,
    RIGHT
  }

  public enum ValidateStage {
    SELECT,
    FROM,
    JOIN,
    WHERE,
    GROUPBY,
    HAVING
  }

  // Constants for all functions
  // window func
  public static final String TUMBLINGWINDOW = "tumblingwindow"; // tumblingwindow(unit, size)
  public static final String HOPPINGWINDOW  = "hoppingwindow";  // hoppingwindow(unit, size, hopSize)
  public static final String SLIDINGWINDOW  = "slidingwindow";  // slidingwindow(unit, size)
  public static final String SESSIONWINDOW  = "sessionwindow";  // sessionwindow(unit, maxsize, timeouts)
}