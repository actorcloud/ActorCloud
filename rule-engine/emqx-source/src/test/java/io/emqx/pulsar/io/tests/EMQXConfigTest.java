package io.emqx.pulsar.io.tests;

import java.util.HashMap;
import java.util.Map;

import io.emqx.pulsar.io.EMQXConfig;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

public class EMQXConfigTest {

  @DataProvider(name = "configs")
  public Object[][] createData() {
    Map<String, Object> correctConf = new HashMap<>();
    correctConf.put("inputTopics", "sample/abc");
    correctConf.put("ruleId", "rule1");
    EMQXConfig emqxConf = new EMQXConfig();
    emqxConf.setBrokerUrl("tcp://localhost:1883").setInputTopics("sample/abc").setRuleId("rule1");

    Map<String, Object> redundantConf = new HashMap<>();
    redundantConf.put("inputTopics", "sample/abc;sample/dce");
    redundantConf.put("unrelated", "nothing");
    redundantConf.put("ruleId", "rule2");
    EMQXConfig emqxConf2 = new EMQXConfig();
    emqxConf2.setBrokerUrl("tcp://localhost:1883").setInputTopics("sample/abc;sample/dce").setRuleId("rule2");

    return new Object[][] {
            { correctConf, emqxConf },
            { redundantConf, emqxConf2 }
    };
  }

  @Test(dataProvider = "configs")
  public void testLoad(Map<String, Object> conf, EMQXConfig emqxConf) {
    Assert.assertEquals(EMQXConfig.load(conf), emqxConf);
  }
}
