package io.emqx.stream.common;

import io.emqx.stream.common.sql.validator.StreamSqlValidator;
import net.sf.jsqlparser.JSQLParserException;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.select.Select;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

public class TestSqlValidator {

  private StreamSqlValidator validator;

  @BeforeClass
  public void setup(){
    validator = new StreamSqlValidator();
  }

  @Test
  public void testValidSql() throws JSQLParserException {
    String sql = "SELECT color FROM sample$$abc where temperature > 25.0";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by color";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color, count(*) as count FROM sample$$abc where temperature > 25.0 group by color";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by color,tumblingwindow('ss', 4)";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color FROM sample$$abc where temperature > 25.0 group by hoppingwindow('ss', 4, 2)";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select topic1.color, t2.humidity from topic1,topic2 as t2 where topic1.ts = t2.ts and topic1.temperature > 25.0";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select color, humidity from topic1 inner join topic2 on topic1.ts = topic2.ts where temperature > 25.0";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select * from topic where payload$$hum > lag(payload$$hum)";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select *  from topic where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*) >= 2";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select * from topic where payload$$hum > lag(payload$$hum) group by slidingwindow('ss', 2) having count(*)=size()";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select * from (select * from actorcloud where device_id = 'client_id_1') where payload$$hum > 73";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select hum, GetMetadataPropertyValue(ac,'topic') as topic from \"actorcloud/#\" as ac where hum > 73";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color FROM sample$$abc where NOT (temperature > 25.0)";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color,unnest(temps) FROM sample$$abc";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color, c.temp FROM parent as p JOIN Lateral (SELECT unnest(p.temps) as temp) as c where c.temp > 27.5";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "SELECT color FROM sample$$abc where color IN ('red','yellow')";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select * from actorcloud where inCircle(payload$$lat,payload$$lng,39.9,118.38,1968.1)";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select * from actorcloud where inPolygon(payload$$lat,payload$$lng,'[[39.944148,116.391279,],[39.897416,116.35111],[39.896802,116.495135]]')";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));

    sql = "select split_part(getMetadataPropertyValue('/mqtt/CYzWtxrql/23314b/2e066eb9684f71f6b104e489e826525e/world','topic'),'/',5) as device_id from sample$$abc";
    Assert.assertTrue(validator.validate((Select) CCJSqlParserUtil.parse(sql)));
  }

  @Test
  public  void testInvalidSql()  throws JSQLParserException  {
    String sql = "SELECT color FROM sample$$abc where temperature BETWEEN 25 AND 26";
    try{
      validator.validate((Select) CCJSqlParserUtil.parse(sql));
      Assert.fail("Should have exception");
    }catch(RuntimeException exp){
      Assert.assertEquals(exp.getMessage(), "Expression temperature BETWEEN 25 AND 26 is not supported");
    }

    sql = "SELECT color FROM sample$$abc,dec where temp>25";
    try{
      validator.validate((Select) CCJSqlParserUtil.parse(sql), true);
      Assert.fail("Should have exception");
    }catch(RuntimeException exp){
      Assert.assertEquals(exp.getMessage(), "Select from multiple topics must be inside a window");
    }

    sql = "SELECT color FROM sample$$abc where slidingwindow('ss', 2)";
    try{
      validator.validate((Select) CCJSqlParserUtil.parse(sql));
      Assert.fail("Should have exception");
    }catch(RuntimeException exp){
      Assert.assertEquals(exp.getMessage(), "FUNCTION slidingwindow cannot be used at WHERE");
    }
  }
}
