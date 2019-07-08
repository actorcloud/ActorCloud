package io.emqx.pulsar.functions;

import io.emqx.stream.common.JsonParser;
import io.emqx.stream.common.internal.MockContext;
import io.emqx.stream.common.internal.MockGenericRecord;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.util.*;

public class TestRuleFunction {
  @Test
  public void testStringRule() throws Exception {
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT ts FROM sample$$abc where temperature" +
            " > 25.0\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);
    StringRuleFunction crf = new StringRuleFunction();
    crf.process("/lwm2m/tenant_id1/product_id1/device_id_1/dn/19/0/0%;{\"temperature\":35,\"ts\":1541152485013}%;1541152485013", context);
    Assert.assertEquals(context.getResult(), "{\"action\":\"newfile\",\"values\":[{\"ts\":1.541152485013E12}]}");
    context.clean();
  }

  @Test
  public void testInvalidInput() throws Exception {
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT ts FROM sample$$abc where temperature" +
            " > 25.0\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);
    StringRuleFunction crf = new StringRuleFunction();
    crf.process("/lwm2m/tenant_id1/product_id1/device_id_1/dn/19/0/0%;{\"temperature\":35," +
            "\"ts\":1541152485013}%;1541152485013", context);
    Assert.assertEquals(context.getResult(), "{\"action\":\"newfile\",\"values\":[{\"ts\":1.541152485013E12}]}");
    context.clean();
    crf.process("/lwm2m/tenant_id1/product_id1/device_id_1/dn/19/0/0%;{\"temperture\":35," +
            "\"ts\":1541152485013}%;1541152485013", context);
    Assert.assertNull(context.getResult());
    context.clean();
    crf.process("/lwm2m/tenant_id1/product_id1/device_id_1/dn/19/0/0%;{\"temperature\":25.12," +
            "\"ts\":1541152485033}%;1541152485033", context);
    Assert.assertEquals(context.getResult(), "{\"action\":\"newfile\",\"values\":[{\"ts\":1.541152485033E12}]}");
  }

  @Test
  public void testComplex() throws Exception {
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT color FROM sample$$abc where " +
            "temperature > 25.0\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);
    RuleFunction crf = new RuleFunction();
    crf.process(new MockGenericRecord("{\"color\":\"red\",\"temperature\":25.2}"), context);
    Assert.assertEquals(context.getResult(), "{\"action\":\"newfile\",\"values\":[{\"color\":\"red\"}]}");
    context.clean();
    crf.process(new MockGenericRecord("{\"color\":\"blue\",\"temperature\":24.9}"), context);
    Assert.assertNull(context.getResult());
    context.clean();
  }

  @Test
  public void testLastRow() throws Exception {
    // Test last row
    List<Map<String, Object>> messages = fillACMessages();
    RuleFunction crf = new RuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule( "{\"sql\":\"select * from topic where payload$$hum > lag" +
            "(payload$$hum)\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    crf.process(new MockGenericRecord(messages.get(0)), context);
    Assert.assertNull(context.getResult());
    context.clean();
    crf.process(new MockGenericRecord(messages.get(1)), context);
    Assert.assertEquals(context.getResult(),
            "{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(2)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(3)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(4)), context);
    Assert.assertNull(context.getResult());
    context.clean();
  }

  @Test
  public void testSession() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    RuleFunction crf = new RuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select * from topic cmc where payload$$hum > lag" +
            "(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 2\"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    crf.process(new MockGenericRecord(messages.get(0)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(1)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(2)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(3)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(4)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();
  }

  @Test
  public void testAllPass() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    RuleFunction crf = new RuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule(
    "{\"sql\":\"select * from topic where payload$$hum > lag(payload$$hum) group by " +
            "slidingwindow('ss', 2) having count(*)=size()\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    crf.process(new MockGenericRecord(messages.get(0)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(1)), context);
    Assert.assertEquals(context.getResult(), "{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(2)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(3)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_2\",\"qos\":1.0,\"payload\":{\"hum\":75.9,\"temp\":13.4},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0},{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(4)), context);
    Assert.assertNull(context.getResult());
    context.clean();
  }

  @Test
  public void testTumble() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringWindowRuleFunction crf = new StringWindowRuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select * from actorcloud where payload$$hum " +
                    "> 65 group by tumblingwindow('tt', 2)\",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    List<String> messageWindow = new LinkedList<>();
    messageWindow.add("actorcloud%;" + JsonParser.toJson(messages.get(0)) + "%;" + messages.get(0).get("__ts"));
    messageWindow.add("actorcloud%;" + JsonParser.toJson(messages.get(1)) + "%;" + messages.get(1).get("__ts"));
    crf.process(messageWindow, context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U6\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":67.1,\"temp\":2.2},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();
  }

//	@Test
//	public void testFilteredSession() throws Exception {
//		List<Map<String, Object>> messages = fillACMessages();
//		RuleFunction crf = new RuleFunction();
//		Map<String, Object> userConfigMap = new HashMap<String, Object>();
//		userConfigMap.put("rule", "{\"sql\":\"select * from (select * from actorcloud where device_id = 'client_id_1') where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 2\",\"actions\":{\"file\":\"newfile\"}}");
//		MockContext context = new MockContext(userConfigMap);
//		
//		crf.process(new MockGenericRecord(messages.get(0)), context);
//		Assert.assertNull(context.getResult());
//		context.clean();
//		
//		crf.process(new MockGenericRecord(messages.get(1)), context);
//		Assert.assertNull(context.getResult());
//		context.clean();
//		
//		crf.process(new MockGenericRecord(messages.get(2)), context);
//		Assert.assertNull(context.getResult());
//		context.clean();
//		
//		crf.process(new MockGenericRecord(messages.get(3)), context);
//		Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0,\"ts\":1.54177568E9}}");
//		context.clean();
//		
//		crf.process(new MockGenericRecord(messages.get(4)), context);
//		Assert.assertNull(context.getResult());
//		context.clean();
//	}

  @Test
  public void testFiltered2() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    RuleFunction crf = new RuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select * from (select * from actorcloud " +
            "where device_id = 'client_id_1') where payload$$hum > 65 and payload$$temp > 12\"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    crf.process(new MockGenericRecord(messages.get(0)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(1)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(2)), context);
    Assert.assertNull(context.getResult());
    context.clean();

    crf.process(new MockGenericRecord(messages.get(3)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":76.5,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();

    crf.process(new MockGenericRecord(messages.get(4)), context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,\"payload\":{\"hum\":73.4,\"temp\":16.5},\"product_id\":\"M3tlTf\",\"topic\":\"test_topic\",\"$$topic\":\"faketopic\",\"type\":1.0}]}");
    context.clean();
  }

  @Test
  public void testCircle() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringRuleFunction crf = new StringRuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select * from actorcloud " +
            "where inCircle(payload$$lat,payload$$lng,39.9078,116.3970,1968.1)\"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    String message = "actorcloud%;" + JsonParser.toJson(messages.get(0)) + "%;1541152485013";
    crf.process(message, context);
    Assert.assertNotNull(context.getResult());
    context.clean();
  }

  @Test
  public void testPolygon() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringRuleFunction crf = new StringRuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select * from actorcloud " +
            "where inPolygon(payload$$lat,payload$$lng,'[[39.944148,116.391279],[39.897416,116.35111],[39.896802,116.495135]]')\"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    String message = "actorcloud%;" + JsonParser.toJson(messages.get(0)) + "%;1541152485013";
    crf.process(message, context);
    Assert.assertNotNull(context.getResult());
    context.clean();
  }

  @Test
  public void testSplitPart() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringRuleFunction crf = new StringRuleFunction();
//    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select split_part('/mqtt/CYzWtxrql/23314b/2e066eb9684f71f6b104e489e826525e/world','/',5) as device_id from actorcloud  \"," +
//            "\"actions\":[{\"file\":\"newfile\"}]}");
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"select split_part(getMetadataPropertyValue('/mqtt/CYzWtxrql/23314b/2e066eb9684f71f6b104e489e826525e/world','topic'),'/',5) as device_id from sample$$abc \"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    String message = "/mqtt/CYzWtxrql/23314b/2e066eb9684f71f6b104e489e826525e/world%;" + JsonParser.toJson(messages.get(0)) + "%;1541152485013";
    crf.process(message, context);
    Assert.assertEquals(context.getResult(),"{\"action\":\"newfile\",\"values\":[{\"device_id\":\"2e066eb9684f71f6b104e489e826525e\"}]}");
    context.clean();
  }


  @Test
  public void testCircleRule() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringRuleFunction crf = new StringRuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT getmetadatapropertyvalue('/+/Cix8aXWVD/#','topic') as topic,*  from \\\"/+/Cix8aXWVD/#\\\" WHERE inCircle(payload$$lat, payload$$lng, 39.919466, 116.383022, 6120.046666502684) AND split_part(getMetadataPropertyValue('/+/Cix8aXWVD/#', 'topic'), '/' ,5) in ('e9142e08965ed4d9d1d016e342d983920402') \",\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    String message = "/mqtt/Cix8aXWVD/84a852/e9142e08965ed4d9d1d016e342d983920402/car_gps%;" + JsonParser.toJson(messages.get(0)) + "%;1541152485013";
    crf.process(message, context);
    Assert.assertNotNull(context.getResult());
    context.clean();
  }


  @Test
  public void testPolygonRule() throws Exception {
    List<Map<String, Object>> messages = fillACMessages();
    StringRuleFunction crf = new StringRuleFunction();
    Map<String, Object> userConfigMap = JsonParser.parseRule("{\"sql\":\"SELECT getmetadatapropertyvalue('/+/Cix8aXWVD/#','topic') as topic,*  from \\\"/+/Cix8aXWVD/#\\\"" +
            " WHERE inPolygon(payload$$lat, payload$$lng, '[[39.938655,116.377031],[39.912985,116.351797],[39.902977,116.439345],[39.937997,116.450503]]') " +
            "AND split_part(getMetadataPropertyValue('/+/Cix8aXWVD/#', 'topic'), '/' ,5) in ('7d412796278e98612e27e149719514de7179') \"," +
            "\"actions\":[{\"file\":\"newfile\"}]}");
    MockContext context = new MockContext(userConfigMap);

    String message = "/mqtt/Cix8aXWVD/84a852/7d412796278e98612e27e149719514de7179/car_gps%;" + JsonParser.toJson(messages.get(0)) + "%;1541152485013";
    crf.process(message, context);
    Assert.assertNotNull(context.getResult());
    context.clean();
  }

// --Commented out by Inspection START (2019/4/10 0010 上午 10:29):
//  public void testFiltered() throws Exception {
//    List<String> messages = new ArrayList<>(Arrays.asList(
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":65.05,\"temp\":24.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485022}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":64.27,\"temp\":24.16},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485220}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":64.04,\"temp\":24.12},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485418}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":63.83,\"temp\":24.1},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485612}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":64.35,\"temp\":24.01},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152485808}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":64.66,\"temp\":24.05},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486002}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":65.3,\"temp\":24.0},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486200}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":64.31,\"temp\":23.7},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486398}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":62.69,\"temp\":23.53},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486596}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":61.64,\"temp\":23.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486790}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":62.93,\"temp\":22.92},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152486988}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":63.66,\"temp\":23.12},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487186}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":63.81,\"temp\":23.53},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487379}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":62.79,\"temp\":24.04},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487575}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":61.49,\"temp\":24.55},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487771}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":63.5,\"temp\":24.02},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152487969}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":63.64,\"temp\":24.05},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488168}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":65.03,\"temp\":23.92},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488363}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":65.95,\"temp\":23.84},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488558}",
//            "{\"tenant_id\":\"CXL5197U7\",\"node\":\"emqx@127.0.0.1\",\"protocol\":\"mqtt\",\"device_id\":\"client_id_1\",\"qos\":1.0,"
//                    + "\"payload\":{\"hum\":67.38,\"temp\":23.51},\"product_id\":\"M3tlTg\",\"topic\":\"test_topic\",\"type\":1.0,\"ts\":1541152488777}"
//    ));
//    RuleFunction crf = new RuleFunction();
//    Map<String, Object> userConfigMap = new HashMap<>();
//    userConfigMap.put("sql", "select * from (select * from actorcloud where device_id = 'client_id_1') where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 7");
//    userConfigMap.put("actions", "file");
//    MockContext context = new MockContext(userConfigMap);
//
//    for(String message: messages) {
//      crf.process(new MockGenericRecord(message), context);
//      Assert.assertNull(context.getResult());
//      context.clean();
//    }
//  }
// --Commented out by Inspection STOP (2019/4/10 0010 上午 10:29)


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
    payload.put("lat", 39.917);
    payload.put("lng", 116.397);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1.0);
    input.put("qos", 1.0);
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
    input.put("type", 1.0);
    input.put("qos", 1.0);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541773780L);
    inputs.add(input);
    // 2
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U7");
    input.put("product_id", "M3tlTg");
    input.put("device_id", "client_id_2");
    input.put("topic", "test_topic");
    payload.put("temp", 13.4);
    payload.put("hum", 75.9);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1.0);
    input.put("qos", 1.0);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541775676L);
    inputs.add(input);
    // 3
    input = new HashMap<>();
    payload = new HashMap<>();
    input.put("$$topic", "faketopic");
    input.put("tenant_id", "CXL5197U7");
    input.put("product_id", "M3tlTf");
    input.put("device_id", "client_id_1");
    input.put("topic", "test_topic");
    payload.put("temp", 16.5);
    payload.put("hum", 76.5);
    input.put("payload", payload);
    input.put("protocol", "mqtt");
    input.put("type", 1.0);
    input.put("qos", 1.0);
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
    input.put("type", 1.0);
    input.put("qos", 1.0);
    input.put("node", "emqx@127.0.0.1");
    input.put("__ts", 1541777676L);
    inputs.add(input);

    return inputs;
  }
}
