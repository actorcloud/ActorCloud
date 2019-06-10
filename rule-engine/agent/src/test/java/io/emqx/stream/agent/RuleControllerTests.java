package io.emqx.stream.agent;

import io.emqx.stream.agent.analyzer.RuleFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.pulsar.client.admin.Functions;
import org.apache.pulsar.client.admin.PulsarAdmin;
import org.apache.pulsar.functions.proto.Function;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SuppressWarnings("SameReturnValue")
@RunWith(SpringRunner.class)
@WebMvcTest(RuleController.class)
public class RuleControllerTests {

  @Value("${pulsar.ruleJar}")
  private String ruleJar;

  @Value("${pulsar.tenant}")
  private String tenant;

  @Value("${pulsar.namespace}")
  private String namespace;

  @Value("${pulsar.ruleClass}")
  private String className;
  @Value("${pulsar.windowRuleClass}")
  private String windowClassName;


  @MockBean
  private PulsarAdmin pulsarAdmin;

  @Mock
  private Functions functions;

  @Autowired
  private MockMvc mvc;

  @Autowired
  private
  ObjectMapper objectMapper;

  @Before
  public void setup(){
    MockitoAnnotations.initMocks(this);
    Mockito.when(pulsarAdmin.functions()).thenReturn(functions);
  }

  @Test
  public void getRules() throws Exception {
    List<String> resultList = new LinkedList<>();
    resultList.add("__rule_rule1");
    Mockito.when(functions.getFunctions(tenant, namespace))
            .thenReturn(resultList);

    MvcResult result = mvc.perform(get("/rules/")
            .contentType(MediaType.APPLICATION_JSON))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isOk())
            .andExpect(content().json("[\"rule1\"]"));
  }

  @Test
  public void createSimpleRule() throws Exception {
    Rule rule = new Rule("rule1", "SELECT * FROM __actorcloud", new ArrayList<>(), true);
    RuleFeature feature = new RuleFeature().windowType(0);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(className, tenant, namespace,
            rule, "persistent://public/default/__actorcloud", false, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(post("/rules/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isCreated())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void createRegexRule() throws Exception {
    Rule rule = new Rule("rule2", "SELECT * FROM \"/mqtt/tenant_id1/product_id1/#\"", new ArrayList<>(), false);
    RuleFeature feature = new RuleFeature().windowType(0);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(className, tenant, namespace,
            rule, "persistent://public/default/%%mqtt%%tenant_id1%%product_id1%%.+", true, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(post("/rules/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isCreated())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void createPlusRule() throws Exception {
    Rule rule = new Rule("rule2", "SELECT * FROM \"/+/tenant_id1/product_id1/+/device_id1/#\"", new ArrayList<>(),
            true);
    RuleFeature feature = new RuleFeature().windowType(0);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(className, tenant, namespace,
            rule, "persistent://public/default/%%((?!%%).)+%%tenant_id1%%product_id1%%((?!%%).)+%%device_id1%%.+", true, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(post("/rules/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isCreated())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void updateSimpleRule() throws Exception {
    Rule rule = new Rule("rule1", "SELECT * FROM \"/lmw2m/tenantid/productid\"", new ArrayList<>(), false);
    RuleFeature feature = new RuleFeature().windowType(0);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(className, tenant, namespace,
            rule, "persistent://public/default/%%lmw2m%%tenantid%%productid", false, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(put("/rules/rule1")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isOk())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void stopRule() throws Exception {
    MvcResult result = mvc.perform(put("/rules/rule1/stop"))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isOk());
  }

  @Test
  public void startRule() throws Exception {
    MvcResult result = mvc.perform(put("/rules/rule1/start"))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isOk());
  }

  @Test
  public void createWindowRule() throws Exception {
    Rule rule = new Rule("rule1", "SELECT * FROM __actorcloud Group By tumblingwindow('ss', 2)", new ArrayList<>(),
            true);
    RuleFeature feature = new RuleFeature().windowType(1).windowLength(2000);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(windowClassName, tenant, namespace,
            rule, "persistent://public/default/__actorcloud", false, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(post("/rules/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isCreated())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void updateWindowRule() throws Exception {
    Rule rule = new Rule("rule1", "SELECT * FROM __actorcloud Group By hoppingwindow('tt', 30, 10)", new ArrayList<>(),
            true);
    RuleFeature feature = new RuleFeature().windowType(2).windowLength(30).windowInterval(10);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(windowClassName, tenant, namespace,
            rule, "persistent://public/default/__actorcloud", false, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(put("/rules/rule1")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isOk())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }

  @Test
  public void createSessionRule() throws Exception {
    Rule rule = new Rule("rule1", "SELECT * FROM __actorcloud Group By sessionwindow('ss', 20, 5)", new ArrayList<>(),
            true);
    RuleFeature feature = new RuleFeature().windowType(2).windowLength(20000).windowInterval(5000);
    Function.FunctionDetails functionDetails = RuleController.createFunctionDetails(windowClassName, tenant, namespace,
            rule, "persistent://public/default/__actorcloud", false, feature);
    Mockito.doAnswer(invocation -> {
      Object arg0 = invocation.getArgument(0);
      Object arg1 = invocation.getArgument(1);

      assertEquals(functionDetails, arg0);
      assertEquals(ruleJar, arg1);
      return null;
    }).when(functions).createFunction(any(Function.FunctionDetails.class), any(String.class));

    MvcResult result = mvc.perform(post("/rules/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(rule)))
            .andReturn();

    mvc.perform(asyncDispatch(result))
            .andExpect(status().isCreated())
            .andExpect(content().json(objectMapper.writeValueAsString(rule)));
  }
}

