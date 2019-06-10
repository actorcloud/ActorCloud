package io.emqx.stream.common;

import io.emqx.stream.common.internal.MockLogger;
import io.emqx.stream.common.sql.ISqlEngine;
import io.emqx.stream.common.sql.SqlEngine;
import net.sf.jsqlparser.JSQLParserException;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.util.*;

public class TestSqlProcessor {

  private MockLogger logger;
  private ISqlEngine sqlProcessor;
  private Map<String, Object> message;
  private Map<String, Object> expected;

  @BeforeClass
  public void beforeMethod() {
    logger = new MockLogger();
  }

  @Test
  public void testCommon() throws Exception {
    String sql = "SELECT color FROM sample$$abc where temperature > 25.0";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    Map<String, Object> result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("color", "red");
    Assert.assertEquals(result, expected);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 24);
    List<Map<String, Object>> results = sqlProcessor.process(message);
    Assert.assertTrue(results.isEmpty());

    sql = "SELECT * FROM sample$$abc where temperature > 25.0";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("temperature", 25.2);
    Assert.assertEquals(result, expected);

    //TODO test select aggregate func
  }

  @Test
  public void testGroup() throws Exception {
    List<Map<String, Object>> results;
    String sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by color";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> messages = fillMessages();
    List<Map<String, Object>> expects = new ArrayList<>();

    results = sqlProcessor.process(messages);
    expected = new HashMap<>();
    expected.put("color", "red");
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);

    sql = "SELECT color, count(*) as count FROM sample$$abc where temperature > 25.0 group by color";
    sqlProcessor = new SqlEngine(sql, logger);
    results = sqlProcessor.process(messages);

    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("count", 1L);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "blue");
    expected.put("count", 2L);
    expects.add(expected);
    Assert.assertEquals(results, expects);

    sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by color having count(*) > 1";
    sqlProcessor = new SqlEngine(sql, logger);
    results = sqlProcessor.process(messages);

    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testTumbleWindow() throws Exception {
    String sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by color,tumblingwindow('ss', 4)";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> messages = fillMessages();
    List<Map<String, Object>> window = new ArrayList<>();
    window.add(messages.get(0));
    window.add(messages.get(1));
    window.add(messages.get(2));
    List<Map<String, Object>> results = sqlProcessor.process(window);
    List<Map<String, Object>> expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);

    window = new ArrayList<>();
    window.add(messages.get(3));
    window.add(messages.get(4));
    window.add(messages.get(5));
    results = sqlProcessor.process(window);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testHoppingWindow() throws Exception {
    String sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by hoppingwindow('ss', 4, 2)";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> messages = fillMessages();
    List<Map<String, Object>> window = new ArrayList<>();
    window.add(messages.get(0));
    window.add(messages.get(1));
    window.add(messages.get(2));
    List<Map<String, Object>> results = sqlProcessor.process(window);
    List<Map<String, Object>> expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);

    window = new ArrayList<>();
    window.add(messages.get(1));
    window.add(messages.get(2));
    window.add(messages.get(3));
    results = sqlProcessor.process(window);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    Assert.assertEquals(results, expects);

    window = new ArrayList<>();
    window.add(messages.get(3));
    window.add(messages.get(4));
    window.add(messages.get(5));
    results = sqlProcessor.process(window);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "red");
    expects.add(expected);
    Assert.assertEquals(results, expects);
  }

  private List<Map<String, Object>> fillMessages() {
    List<Map<String, Object>> messages = new ArrayList<>();
    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 22.2);
    message.put("__ts", 1541769447L);
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "yellow");
    message.put("temperature", 24.9);
    message.put("__ts", 1541769455L);
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "blue");
    message.put("temperature", 28L);
    message.put("__ts", 1541769466L);
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "yellow");
    message.put("temperature", 24L);
    message.put("__ts", 1541769477L);
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "blue");
    message.put("temperature", 27.2);
    message.put("__ts", 1541769488L);
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.3);
    message.put("__ts", 1541769499L);
    messages.add(message);

    return messages;
  }

  @Test
  public void testJoinByWhere() throws Exception {
    String sql = "select topic1.color, t2.humidity from topic1,topic2 as t2 where topic1.ts = t2.ts and topic1.temperature > 25.0";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> messages = fillMultiTopicMessages();
    List<Map<String, Object>> window = new ArrayList<>();
    window.add(messages.get(0));
    window.add(messages.get(1));
    window.add(messages.get(2));
    window.add(messages.get(3));
    window.add(messages.get(4));
    window.add(messages.get(5));
//    List<Map<String, Object>> results;
    List<Map<String, Object>> results = sqlProcessor.process(window);
    List<Map<String, Object>> expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("topic1.color", "blue");
    expected.put("t2.humidity", 69.4);
    expects.add(expected);
    Assert.assertEquals(results, expects);

    sql = "select color, humidity from topic1 inner join topic2 on topic1.ts = topic2.ts where temperature > 25.0";
    sqlProcessor = new SqlEngine(sql, logger);
    messages = fillMultiTopicMessages();
    window = new ArrayList<>();
    window.add(messages.get(0));
    window.add(messages.get(1));
    window.add(messages.get(2));
    window.add(messages.get(3));
    window.add(messages.get(4));
    window.add(messages.get(5));
    results = sqlProcessor.process(window);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "blue");
    expected.put("humidity", 69.4);
    expects.add(expected);
    Assert.assertEquals(results, expects);

    sql = "select color, humidity from topic1 outer join topic2 on topic1.ts = topic2.ts where temperature > 25.0";
    sqlProcessor = new SqlEngine(sql, logger);
    messages = fillMultiTopicMessages();
    results = sqlProcessor.process(messages);
    Assert.assertEquals(results.size(), 3);

    sql = "select color, humidity from topic1 left join topic2 on topic1.ts = topic2.ts";
    sqlProcessor = new SqlEngine(sql, logger);
    messages = fillMultiTopicMessages();
    results = sqlProcessor.process(messages);
    Assert.assertEquals(results.size(), 6);

    sql = "select color, humidity from topic1 left join topic2";
    sqlProcessor = new SqlEngine(sql, logger);
    messages = fillMultiTopicMessages();
    results = sqlProcessor.process(messages);
    Assert.assertEquals(results.size(), 36);
  }

  private List<Map<String, Object>> fillMultiTopicMessages() {
    List<Map<String, Object>> messages = new ArrayList<>();
    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 22.2);
    message.put("ts", 1541769447L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 75.2);
    message.put("ts", 1541769447L);
    message.put("__topic", "topic2");
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "yellow");
    message.put("temperature", 24.9);
    message.put("ts", 1541769455L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 76.3);
    message.put("ts", 1541769455L);
    message.put("__topic", "topic2");
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "blue");
    message.put("temperature", 28.0);
    message.put("ts", 1541769466L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 69.4);
    message.put("ts", 1541769466L);
    message.put("__topic", "topic2");
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "yellow");
    message.put("temperature", 24.0);
    message.put("ts", 1541769477L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 68.5);
    message.put("ts", 1541769477L);
    message.put("__topic", "topic2");
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "blue");
    message.put("temperature", 27.2);
    message.put("ts", 1541769488L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 70.9);
    message.put("ts", 1541769497L);
    message.put("__topic", "topic2");
    messages.add(message);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.3);
    message.put("ts", 1541769499L);
    message.put("__topic", "topic1");
    messages.add(message);

    message = new HashMap<>();
    message.put("humidity", 71.2);
    message.put("ts", 1541769499L);
    message.put("__topic", "topic2");
    messages.add(message);

    return messages;
  }


  @Test
  public void testTopic() throws Exception {
    String sql = "SELECT color FROM sample$$abc where __topic = 'actorcloud'";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> results;

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    message.put("__topic", "actorcloud");
    results = sqlProcessor.process(message);
    expected = new HashMap<>();
    expected.put("color", "red");
    Assert.assertEquals(expected, results.get(0));

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 24.9);
    message.put("__topic", "actorcloud2");
    results = sqlProcessor.process(message);
    Assert.assertEquals(results.size(), 0);
  }

  @Test
  public void testLastRow() throws Exception {
    String sql = "select * from topic where payload$$hum > lag(payload$$hum)";
    sqlProcessor = new SqlEngine(sql, logger);
    // Test last row
    List<Map<String, Object>> messages = fillACMessages();
    List<Map<String, Object>> expects = expected4LastRow(fillACMessages());
    List<Map<String, Object>> results = sqlProcessor.process(messages);
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testSession() throws Exception {
    String sql = "select *  from topic where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 2";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> expects = expected4Session(fillACMessages());
    List<Map<String, Object>> results = null;
    for (Map<String, Object> message : fillACMessages()) {
      results = sqlProcessor.process(message);
    }
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testAllPass() throws Exception {
    String sql = "select * from topic where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*)=size()";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> expects = expected4AllPass(fillACMessages());
    List<Map<String, Object>> results = null;
    int count = 0;
    for (Map<String, Object> message : fillACMessages()) {
      count++;
      if(count > 4 ) break;
      results = sqlProcessor.process(message);
    }

    Assert.assertEquals(results, expects);
  }

  @Test
  public void testFilteredSession() throws Exception {
    String sql = "select * from actorcloud where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 2";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> expects = expected4AllPass(fillACMessages());
    List<Map<String, Object>> results = null;
    for (Map<String, Object> message : fillACMessages()) {
      results = sqlProcessor.process(message);
    }
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testF2CFunction() throws Exception {
    String sql = "select ftoc(temperature) from actorcloud";
    Map<String, Object> result;
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 212L);
    message.put("__topic", "actorcloud");
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("ftoc", 100.0);
    Assert.assertEquals(result, expected);

    sql = "select ctof(payload$$temp) as mytemp from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    Map<String, Object> payload = new HashMap<>();
    message.put("$$topic", "faketopic");
    message.put("tenant_id", "CXL5197U6");
    message.put("product_id", "M3tlTf");
    message.put("device_id", "client_id_1");
    message.put("topic", "test_topic");
    payload.put("temp", 30.1);
    payload.put("hum", 30L);
    message.put("payload", payload);
    message.put("protocol", "mqtt");
    message.put("type", 1);
    message.put("qos", 1);
    message.put("node", "emqx@127.0.0.1");
    message.put("ts", 1541769447L);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("mytemp", 86.18);
    Assert.assertEquals(result, expected);
  }

  @Test
  public void testSelectLevel() throws Exception {
    String sql = "select payload$$temp from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    Map<String, Object> payload = new HashMap<>();
    Map<String, Object> result;

    message.put("$$topic", "faketopic");
    message.put("tenant_id", "CXL5197U6");
    message.put("product_id", "M3tlTf");
    message.put("device_id", "client_id_1");
    message.put("topic", "test_topic");
    payload.put("temp", 30.1);
    payload.put("hum", 30);
    message.put("payload", payload);
    message.put("protocol", "mqtt");
    message.put("type", 1);
    message.put("qos", 1);
    message.put("node", "emqx@127.0.0.1");
    message.put("ts", 1541769447L);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    Map<String, Object> expectedPayload = new HashMap<>();
    expectedPayload.put("temp", 30.1);
    expected.put("payload", expectedPayload);
    Assert.assertEquals(result, expected);

    sql = "select payload$$temp as payload$$temp2 from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expectedPayload = new HashMap<>();
    expectedPayload.put("temp2", 30.1);
    expected.put("payload", expectedPayload);
    Assert.assertEquals(result, expected);

    sql = "select payload$$temp as payload$$temp2$$celsius from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expectedPayload = new HashMap<>();
    Map<String, Object> expectedTemp = new HashMap<>();
    expectedTemp.put("celsius", 30.1);
    expectedPayload.put("temp2", expectedTemp);
    expected.put("payload", expectedPayload);
    Assert.assertEquals(result, expected);

    Map<String, Object> temp = new HashMap<>();
    temp.put("celsius", 28.3);
    payload.put("cel", temp);
    message.put("payload", payload);
    sql = "select payload$$cel$$celsius as celsius from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("celsius", 28.3);
    Assert.assertEquals(result, expected);

    sql = "select temps$$1 as t2 from actorcloud";
    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[25.3,27.5,28.1]}");
    sqlProcessor = new SqlEngine(sql, logger);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("t2", 27.5);
    Assert.assertEquals(result, expected);
  }

  @Test
  public void testArithmetic() throws Exception {
    String sql = "select (5 + 32.1 * 3) as result from actorcloud";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    message.put("nothing", "nothing");
    Map<String, Object> result = sqlProcessor.process(message).get(0);
    Map<String, Object> expected = new HashMap<>();
    expected.put("result", 5 + 32.1 * 3);
    Assert.assertEquals(result, expected);
  }

  @Test
  public void testInvalidMessage() throws JSQLParserException {
    String sql = "select * from actorcloud where payload$$hum > payload$$temp";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    try{
      sqlProcessor.process(message);
      Assert.fail("Should have exceptions");
    }catch(Exception ex){
      Assert.assertTrue(true);
    }
  }

  @Test
  public void testFilterdLastRow() throws Exception {
    String sql = "select * from (select * from actorcloud where device_id = 'client_id_1') where payload$$hum > 73";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> expects = expected4FilteredLastRow(fillACMessages());
    List<Map<String, Object>> results = null;
    for (Map<String, Object> message : fillACMessages()) {
      results = sqlProcessor.process(message);
    }
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testMetaProperty() throws Exception {
    String sql = "select hum, GetMetadataPropertyValue(ac,'topic') as topic from \"actorcloud/#\" as ac where" +
            " hum > 73";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    message.put("color", "red");
    message.put("hum", 75.3);
    message.put("__topic","actorcloud/topic1");
    Map<String, Object> result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("hum", 75.3);
    expected.put("topic", "actorcloud/topic1");
    Assert.assertEquals(result, expected);

    sql = "select ac.*, GetMetadataPropertyValue(\"actorcloud/#\",'topic') as topic from \"actorcloud/#\" where" +
            " hum > 73";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    message.put("color", "red");
    message.put("hum", 75.3);
    message.put("__topic","actorcloud/topic1");
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("ac.color", "red");
    expected.put("ac.hum", 75.3);
    expected.put("topic", "actorcloud/topic1");
    Assert.assertEquals(result, expected);
  }

  @Test
  public void testNoMessageWindow() throws Exception {
    String sql = "SELECT 'true' as result FROM sample$$abc group by tumblingwindow('ss', 4) having size()=0";
    sqlProcessor = new SqlEngine(sql, logger);

    List<Map<String, Object>> messages = fillMessages();
    List<Map<String, Object>> window = new ArrayList<>();
    window.add(messages.get(0));
    window.add(messages.get(1));
    window.add(messages.get(2));
    List<Map<String, Object>> results = sqlProcessor.process(window);
    List<Map<String, Object>> expects = new ArrayList<>();
    Assert.assertEquals(results, expects);

    window = new ArrayList<>();
    results = sqlProcessor.process(window);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("result", "true");
    expects.add(expected);
    Assert.assertEquals(results, expects);
  }

  @Test
  public void testNot() throws Exception {
    String sql = "SELECT color FROM sample$$abc where NOT (temperature > 25.0)";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    List<Map<String, Object>> result = sqlProcessor.process(message);
    List<Map<String, Object>> expects = new ArrayList<>();
    Assert.assertEquals(result, expects);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 24.9);
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "SELECT color FROM sample$$abc where NOT (temperature > 25.0) and temperature > 23";
    sqlProcessor = new SqlEngine(sql, logger);
    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 23.2);
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expects.add(expected);
    Assert.assertEquals(result, expects);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 22.9);
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    Assert.assertEquals(result, expects);
  }

  @Test
  public void testUnnest() throws Exception {
    String sql = "SELECT color,unnest(temps) FROM sample$$abc";
    sqlProcessor = new SqlEngine(sql, logger);

    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[25.3,27.5,28.1]}");
    List<Map<String, Object>> result = sqlProcessor.process(message);
    List<Map<String, Object>> expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("unnest", 25.3);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("unnest", 27.5);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("unnest", 28.1);
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "SELECT color,unnest(temps, 'outer') as t, unnest(hums,'outer') as h FROM sample$$abc";
    sqlProcessor = new SqlEngine(sql, logger);

    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[], \"hums\":[76, 65]}");
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("t", null);
    expected.put("h", 76.0);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("t", null);
    expected.put("h", 65.0);
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "SELECT color,unnest(temps, 'cross') FROM sample$$abc";
    sqlProcessor = new SqlEngine(sql, logger);

    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[]}");
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    Assert.assertEquals(result, expects);
  }

  @Test
  public void testLateral() throws Exception {
    String sql = "SELECT color, c.temp FROM parent as p JOIN Lateral (SELECT unnest(p.temps) as temp) as c where c.temp > 27.5";
    sqlProcessor = new SqlEngine(sql, logger);

    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[25.3,27.5,28.1]}");
    List<Map<String, Object>> result = sqlProcessor.process(message);
    List<Map<String, Object>> expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("c.temp", 28.1);
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "SELECT color, c.temp FROM parent as a JOIN Lateral (SELECT unnest(parent.temps) as temp from parent where parent.color = a.color) as c where c.temp > 27.5";
    sqlProcessor = new SqlEngine(sql, logger);
    List<Map<String, Object>> messages = new LinkedList<>();
    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[25.3,27.5,28.1]}");
    assert message != null;
    message.put("__topic", "parent");
    messages.add(message);
    message = JsonParser.parseMqttMessage("{\"color\":\"blue\"," +
            "\"temps\":[28.3,26.5,29.1]}");
    assert message != null;
    message.put("__topic", "parent");
    messages.add(message);
    result = sqlProcessor.process(messages);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("color", "red");
    expected.put("c.temp", 28.1);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "blue");
    expected.put("c.temp", 28.3);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("color", "blue");
    expected.put("c.temp", 29.1);
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "SELECT p.color, c.unnest FROM parent p " +
            "INNER JOIN topic1 ON p.color=topic1.color " +
            "INNER JOIN topic2 ON topic1.ts=topic2.ts " +
            "JOIN Lateral (SELECT unnest(p.temps)) c " +
            "WHERE c.unnest > 27.5";
    sqlProcessor = new SqlEngine(sql, logger);

    messages = fillMultiTopicMessages();
    message = JsonParser.parseMqttMessage("{\"color\":\"red\"," +
            "\"temps\":[25.3,27.5,28.1]}");
    assert message != null;
    message.put("__topic", "parent");
    messages.add(message);
    message = JsonParser.parseMqttMessage("{\"color\":\"blue\"," +
            "\"temps\":[28.3,26.5,29.1]}");
    assert message != null;
    message.put("__topic", "parent");
    messages.add(message);
    result = sqlProcessor.process(messages);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("p.color", "red");
    expected.put("c.unnest", 28.1);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("p.color", "red");
    expected.put("c.unnest", 28.1);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("p.color", "blue");
    expected.put("c.unnest", 28.3);
    expects.add(expected);
    expected = new HashMap<>();
    expected.put("p.color", "blue");
    expected.put("c.unnest", 29.1);
    expects.add(expected);
    Assert.assertEquals(result, expects);

    sql = "select 'alert' as alert from topic JOIN LATERAL (SELECT unnest(topic.data$$devices) as device) as c " +
            "where c.device$$data$$mode$$value='cold'";
    sqlProcessor = new SqlEngine(sql, logger);

    message = JsonParser.parseMqttMessage("{\"data_type\":\"events\",\"data\":{\"devices\":[{" +
            "\"device_id\":\"device_id_1\",\"data\":{\"status\":{\"time\":1547661822,\"value\":true}," +
            "\"mode\":{\"time\":1547661822,\"value\":\"cold\"}}},{\"device_id\":\"device_id_2\"," +
            "\"data\":{\"status\":{\"time\":1547661822,\"value\":true}," +
            "\"mode\":{\"time\":1547661822,\"value\":\"cold\"}}}]}}");
    result = sqlProcessor.process(message);
    Assert.assertEquals(result.size(), 2);

    sql = "SELECT c.t FROM \"/jsonup/CYzWtxrql/product2/device2/topic1\" as p join " +
            "lateral (select p.temperature as t) as c";
    sqlProcessor = new SqlEngine(sql, logger);
    message = JsonParser.parseMqttMessage("{\"temperature\":35,\"timestamp\":1541152485013}");
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("c.t", 35.0);
    expects.add(expected);
    Assert.assertEquals(result, expects);
    message = JsonParser.parseMqttMessage("{\"temperature\":29,\"timestamp\":1541152485022}");
    result = sqlProcessor.process(message);
    expects = new ArrayList<>();
    expected = new HashMap<>();
    expected.put("c.t", 29.0);
    expects.add(expected);
    Assert.assertEquals(result, expects);
  }

  private List<Map<String, Object>> fillACMessages() {
    // 0
    List<Map<String, Object>> inputs = new ArrayList<>();
    Map<String, Object> input = new HashMap<>();
    Map<String, Object> payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U6");
    input.put("product_id", "M3tlTf");
    input.put("device_id", "client_id_1");
    input.put("topic", "test_topic");
    payload.put("temp", 32.3);
    payload.put("hum", 30L);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1);
    input.put("qos", 1);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541769447L);
    inputs.add(input);
    // 1
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U6");
    input.put("product_id", "M3tlTf");
    input.put("device_id", "client_id_1");
    input.put("topic", "test_topic");
    payload.put("temp", 2.2);
    payload.put("hum", 67.1);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1);
    input.put("qos", 1);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541771780L);
    inputs.add(input);
    // 2
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U7");
    input.put("product_id", "M3tlTg");
    input.put("device_id", "client_id_1");
    input.put("topic", "test_topic");
    payload.put("temp", 13.4);
    payload.put("hum", 72.9);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1);
    input.put("qos", 1);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541773776L);
    inputs.add(input);
    // 3
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U7");
    input.put("product_id", "M3tlTf");
    input.put("device_id", "client_id_2");
    input.put("topic", "test_topic");
    payload.put("temp", 16.5);
    payload.put("hum", 76.5);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1);
    input.put("qos", 1);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541775680L);
    inputs.add(input);

    // 4
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U7");
    input.put("product_id", "M3tlTf");
    input.put("device_id", "client_id_1");
    input.put("topic", "test_topic");
    payload.put("temp", 16.5);
    payload.put("hum", 73.4);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1);
    input.put("qos", 1);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541775676L);
    inputs.add(input);

    return inputs;
  }

  private List<Map<String, Object>> expected4LastRow(List<Map<String, Object>> inputs) {
    List<Map<String, Object>> expects = new ArrayList<>();

    Map<String, Object> input = inputs.get(1);
    input.remove("__ts");
    expects.add(input);
    input = inputs.get(2);
    input.remove("__ts");
    expects.add(input);
    input = inputs.get(3);
    input.remove("__ts");
    expects.add(input);

    return expects;
  }

  private List<Map<String, Object>> expected4Session(List<Map<String, Object>> inputs) {
    List<Map<String, Object>> expects = new ArrayList<>();
    Map<String, Object> input = inputs.get(2);
    input.remove("__ts");
    expects.add(input);
    input = inputs.get(3);
    input.remove("__ts");
    expects.add(input);
    return expects;
  }

  private List<Map<String, Object>> expected4AllPass(List<Map<String, Object>> inputs) {
    List<Map<String, Object>> expects = new ArrayList<>();
    Map<String, Object> input = inputs.get(2);
    input.remove("__ts");
    expects.add(input);
    input = inputs.get(3);
    input.remove("__ts");
    expects.add(input);
    return expects;
  }

  private List<Map<String, Object>> expected4FilteredLastRow(List<Map<String, Object>> inputs) {
    List<Map<String, Object>> expects = new ArrayList<>();
    Map<String, Object> input = inputs.get(4);
    input.remove("__ts");
    expects.add(input);
    return expects;
  }

  @Test
  public void testIn() throws Exception {
    String sql = "SELECT color FROM sample$$abc where temperature IN (25.0, 25.1, 25.2)";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    Map<String, Object> result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("color", "red");
    Assert.assertEquals(result, expected);

    sql = "SELECT color FROM sample$$abc where color IN ('red','yellow')";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    result = sqlProcessor.process(message).get(0);
    expected = new HashMap<>();
    expected.put("color", "red");
    Assert.assertEquals(result, expected);

    sql = "SELECT color FROM sample$$abc where color NOT IN ('red','yellow')";
    sqlProcessor = new SqlEngine(sql, logger);

    message = new HashMap<>();
    message.put("color", "red");
    message.put("temperature", 25.2);
    List<Map<String, Object>> results = sqlProcessor.process(message);
    Assert.assertEquals(results.size(), 0);
  }

}
