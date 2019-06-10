package io.emqx.stream.agent;

import io.emqx.pulsar.functions.windowing.SessionConfig;
import io.emqx.stream.agent.analyzer.RuleFeature;
import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.analyzer.RuleTablesNameFinder;
import io.emqx.stream.common.sql.validator.StreamSqlValidator;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.LongValue;
import net.sf.jsqlparser.expression.StringValue;
import net.sf.jsqlparser.parser.CCJSqlParserUtil;
import net.sf.jsqlparser.statement.Statement;
import net.sf.jsqlparser.statement.select.PlainSelect;
import net.sf.jsqlparser.statement.select.Select;
import org.apache.pulsar.client.admin.PulsarAdmin;
import org.apache.pulsar.functions.proto.Function;
import org.apache.pulsar.functions.proto.Function.FunctionDetails;
import org.apache.pulsar.functions.proto.InstanceCommunication.FunctionStatusList;
import org.apache.pulsar.functions.utils.WindowConfig;
import org.apache.pulsar.shade.com.google.protobuf.util.JsonFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.context.request.async.DeferredResult;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

@SuppressWarnings("unused")
@RestController
class RuleController {
  private static final Logger logger = LoggerFactory.getLogger(RuleController.class);
  private static final ObjectMapper mapper = new ObjectMapper();
  private static final String NAME_PREFIX = "__rule_";
  public static final String DUMMY_WINDOW_FUNCTION = "com.emqx.pulsar.functions.DummyWindowFunction";

  @Autowired
  private PulsarAdmin pulsarAdmin;

  @Value("${pulsar.ruleJar}")
  private String ruleJar;

  @SuppressWarnings("unused")
  @Value("${pulsar.tenant}")
  private String tenant;

  @SuppressWarnings("unused")
  @Value("${pulsar.namespace}")
  private String namespace;

  @Value("${pulsar.ruleClass}")
  private String className;

  @Value("${pulsar.windowRuleClass}")
  private String windowClassName;

  @RequestMapping(value = "/rules/", method = RequestMethod.POST)
  public DeferredResult<ResponseEntity<?>> createRule(@RequestBody Rule rule) {
    logger.info("Create new rule {}", rule.getId());
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    try{
      RuleFeature feature = analyzeSql(rule.getSql());
      String sourceTopic = String.join(",", feature.topics());

      if(sourceTopic.isEmpty()){
        output.setResult(new ResponseEntity<>("Invalid sql: no FROM entity is found", HttpStatus.BAD_REQUEST));
      }else{
        CompletableFuture.runAsync(() -> {
          try {
            pulsarAdmin.functions().createFunctionWithUrl(createFunctionDetails(feature.windowType() > 0 ? windowClassName : className,
                    tenant, namespace, rule, sourceTopic, sourceTopic.contains("+"), feature), ruleJar);
            if(!rule.isEnabled()){
              pulsarAdmin.functions().stopFunction(tenant, namespace, NAME_PREFIX + rule.getId());
            }
            output.setResult(new ResponseEntity<>(rule, HttpStatus.CREATED));
          } catch (Exception e) {
            e.printStackTrace();
            output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
          }
        });
      }
    } catch (Exception e) {
      e.printStackTrace();
      output.setResult(new ResponseEntity<>(String.format("Invalid sql: %s", e.getMessage()), HttpStatus.BAD_REQUEST));
    }
    return output;
  }
  private RuleFeature analyzeSql(String sql) throws Exception {
    RuleFeature feature = new RuleFeature();
    Select select;
    Statement stmt = CCJSqlParserUtil.parse(sql);
    if(stmt instanceof Select){
      select = (Select) stmt;
    }else{
      throw new RuntimeException("Not a select statement");
    }

    List<String> topics = new RuleTablesNameFinder().getTableList(select);
    //Validate here
    new StreamSqlValidator().validate(select, topics.size() > 1);
    //TODO Always add tenant prefix for now. Make sure the from clause does not have pulsar tenant part
    feature.topics(topics.parallelStream()
            .map(topic -> String.format("persistent://%s/%s/%s", tenant, namespace,
                    topic.replace("\"", "").replace("/","%%").replace("%%+%%",
                            "%%((?!%%).)+%%").replace("#", ".+"))).collect(Collectors.toList()));
    checkWindow(select, feature);
    return feature;
  }

  private void checkWindow(Select select, RuleFeature feature) {
    feature.windowType(0);
    if(select.getSelectBody() instanceof PlainSelect){
      List<Expression> groups = ((PlainSelect) select.getSelectBody()).getGroupByColumnReferences();
      if(groups == null){
        return;
      }
      for(Expression group : groups){
        if(group instanceof net.sf.jsqlparser.expression.Function){
          net.sf.jsqlparser.expression.Function function = (net.sf.jsqlparser.expression.Function) group;
          String name = function.getName().toLowerCase();
          //TODO currently, only one window is allowed
          if(name.equals(Constants.TUMBLINGWINDOW) || name.equals(Constants.HOPPINGWINDOW) || name.equals(Constants.SESSIONWINDOW)){
            List<Expression> params = function.getParameters() != null ? function.getParameters().getExpressions() : new ArrayList<>();
            String unit = ((StringValue)params.get(0)).getValue();
            long windowSize = ((LongValue)params.get(1)).getValue();
            feature.windowType(isDuration(unit) ? 1 : 2);
            feature.windowLength(getWindowSize(unit, windowSize));
            if(params.size() == 3){
              long hopSize = ((LongValue)params.get(2)).getValue();
              feature.windowInterval(getWindowSize(unit, hopSize));
            }
            if(name.equalsIgnoreCase(Constants.SESSIONWINDOW)){
              feature.windowType(2);
            }
            return;
          }
        }
      }
    }
  }

  private boolean isDuration(String unit) {
    return !unit.equals("tt");
  }

  private long getWindowSize(String unit, long size) {
    long result;
    switch(unit){
      case "mc":
        result = size/1000;
        break;
      case "tt":
      case "ms":
        result = size;
        break;
      case "ss":
        result = size * 1000;
        break;
      case "mi":
        result = size * 1000 * 60;
        break;
      case "hh":
        result = size * 1000 * 60 * 60;
        break;
      case "dd":
        result = size * 1000 * 60 * 60 * 24;
        break;
      default:
        throw new RuntimeException("Invalid window unit");
    }
    return result;
  }

  @RequestMapping(value = "/rules/", method = RequestMethod.GET)
  public DeferredResult<ResponseEntity<?>> listAllRules() {
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    CompletableFuture.runAsync(() -> {
      try {
        List<String> functionNames = pulsarAdmin.functions().getFunctions(tenant, namespace);
        final int prefixLength = NAME_PREFIX.length();
        List<String> result = functionNames.stream().filter(name -> name.startsWith(NAME_PREFIX))
                .map(name -> name.substring(prefixLength)).collect(Collectors.toList());
        output.setResult(new ResponseEntity<>(result, HttpStatus.OK));
      } catch (Exception e) {
        e.printStackTrace();
        output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
      }
    });
    return output;
  }

  @RequestMapping(value = "/rules/{id}", method = RequestMethod.GET)
  public DeferredResult<ResponseEntity<?>> getRule(@PathVariable String id) {
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    CompletableFuture.runAsync(() -> {
      try {
        FunctionStatusList status = pulsarAdmin.functions().getFunctionStatus(tenant, namespace, NAME_PREFIX + id);
        String json = JsonFormat.printer().print(status);
        output.setResult(new ResponseEntity<>(json, HttpStatus.OK));
      } catch (Exception e) {
        e.printStackTrace();
        output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
      }
    });
    return output;
  }

  @RequestMapping(value = "/rules/{id}", method = RequestMethod.PUT)
  public DeferredResult<ResponseEntity<?>> updateRule(@PathVariable String id, @RequestBody Rule rule) {
    logger.info("Update rule {}", id);
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    try{
      RuleFeature feature = analyzeSql(rule.getSql());
      String sourceTopic = String.join(",", feature.topics());
      if(sourceTopic.isEmpty()) {
        output.setResult(new ResponseEntity<>("Invalid sql: no FROM entity is found", HttpStatus.BAD_REQUEST));
      }else{
        CompletableFuture.runAsync(() -> {
          try {
            pulsarAdmin.functions().updateFunctionWithUrl(createFunctionDetails(feature.windowType() > 0 ? windowClassName : className,
                    tenant, namespace, rule, sourceTopic, sourceTopic.contains("+"), feature),ruleJar);
            if(!rule.isEnabled()){
              pulsarAdmin.functions().stopFunction(tenant, namespace, NAME_PREFIX + rule.getId());
            }
            output.setResult(new ResponseEntity<>(rule, HttpStatus.OK));
          } catch (Exception e) {
            e.printStackTrace();
            output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
          }
        });
      }
    } catch (Exception e) {
      e.printStackTrace();
      output.setResult(new ResponseEntity<>(String.format("Invalid sql: %s", e.getMessage()), HttpStatus.BAD_REQUEST));
    }
    return output;
  }

  @RequestMapping(value = "/rules/{id}/stop", method = RequestMethod.PUT)
  public DeferredResult<ResponseEntity<?>> stopRule(@PathVariable String id) {
    logger.info("Stop rule {}", id);
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    CompletableFuture.runAsync(() -> {
      try {
        pulsarAdmin.functions().stopFunction(tenant, namespace, NAME_PREFIX + id);
        output.setResult(new ResponseEntity<>(HttpStatus.OK));
      } catch (Exception e) {
        e.printStackTrace();
        output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
      }
    });

    return output;
  }

  @RequestMapping(value = "/rules/{id}/start", method = RequestMethod.PUT)
  public DeferredResult<ResponseEntity<?>> startRule(@PathVariable String id) {
    logger.info("Stop rule {}", id);
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();
    CompletableFuture.runAsync(() -> {
      try {
        pulsarAdmin.functions().restartFunction(tenant, namespace, NAME_PREFIX + id);
        output.setResult(new ResponseEntity<>(HttpStatus.OK));
      } catch (Exception e) {
        e.printStackTrace();
        output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
      }
    });

    return output;
  }

  @RequestMapping(value = "/rules/{id}", method = RequestMethod.DELETE)
  public DeferredResult<ResponseEntity<?>> deleteRule(@PathVariable String id) {
    logger.info("Delete rule {}", id);
    DeferredResult<ResponseEntity<?>> output = new DeferredResult<>();

    CompletableFuture.runAsync(() -> {
      try {
        pulsarAdmin.functions().deleteFunction(tenant, namespace, NAME_PREFIX + id);
        output.setResult(new ResponseEntity<>("OK", HttpStatus.OK));
      } catch (Exception e) {
        e.printStackTrace();
        output.setResult(new ResponseEntity<>(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR));
      }
    });

    return output;
  }

  // For the sake of extension, check FunctionConfigUtils.convert
  static FunctionDetails createFunctionDetails(String className, String tenant, String namespace, Rule rule,
                                               String sourceTopic, boolean isPattern, RuleFeature feature) throws Exception {

    FunctionDetails.Builder functionDetailsBuilder = FunctionDetails.newBuilder();
    functionDetailsBuilder.setTenant(tenant);
    functionDetailsBuilder.setNamespace(namespace);
    functionDetailsBuilder.setName(NAME_PREFIX + rule.getId());
    functionDetailsBuilder.setRuntime(FunctionDetails.Runtime.JAVA);
    functionDetailsBuilder.setParallelism(1);
    functionDetailsBuilder.setClassName(className);
    if(feature.windowType() > 0){
      WindowConfig windowConfig = new WindowConfig();
      SessionConfig sessionConfig = null;
      if(feature.windowType() == 1){ //duration
        windowConfig.setWindowLengthDurationMs(feature.windowLength());
        if(feature.windowInterval() > 0){
          windowConfig.setSlidingIntervalDurationMs(feature.windowInterval());
        }
      }else if(feature.windowType() == 2){ //session window
        sessionConfig = new SessionConfig();
        sessionConfig.setWindowLengthDurationMs(feature.windowLength())
                .setTimeoutlDurationMs(feature.windowInterval());
      }else{ //count
        windowConfig.setWindowLengthCount((int) feature.windowLength());
        if(feature.windowInterval() > 0){
          windowConfig.setSlidingIntervalCount((int) feature.windowInterval());
        }
      }
      windowConfig.setActualWindowFunctionClassName(DUMMY_WINDOW_FUNCTION);
      TypeReference<HashMap<String,Object>> typeRef
              = new TypeReference<HashMap<String,Object>>() {};
      Map<String, Object> configs = mapper.readValue(mapper.writeValueAsString(rule), typeRef);
      configs.put(WindowConfig.WINDOW_CONFIG_KEY, windowConfig);
      if(sessionConfig != null){
        configs.put(Constants.SESSION_CONFIG_KEY, sessionConfig);
      }
      functionDetailsBuilder.setUserConfig(mapper.writeValueAsString(configs));
    }else{
      functionDetailsBuilder.setUserConfig(mapper.writeValueAsString(rule));
    }

    Function.SourceSpec.Builder sourceSpecBuilder = Function.SourceSpec.newBuilder();
    sourceSpecBuilder.putInputSpecs(sourceTopic,
            Function.ConsumerSpec.newBuilder()
                    .setIsRegexPattern(isPattern)
                    .build());
    sourceSpecBuilder.setSubscriptionType(Function.SubscriptionType.SHARED);
    //TODO Infer type, hard code it now for source and sink
    sourceSpecBuilder.setTypeClassName("java.lang.String");
    functionDetailsBuilder.setSource(sourceSpecBuilder);
    Function.SinkSpec.Builder sinkSpecBuilder = Function.SinkSpec.newBuilder();
    sinkSpecBuilder.setTypeClassName("java.lang.Void");
    functionDetailsBuilder.setSink(sinkSpecBuilder);

    functionDetailsBuilder.setAutoAck(true);
    FunctionDetails result = functionDetailsBuilder.build();
    logger.info("Function detail {}", result);
    return result;
  }
}