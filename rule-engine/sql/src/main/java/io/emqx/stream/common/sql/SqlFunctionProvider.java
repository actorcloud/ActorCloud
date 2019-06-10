package io.emqx.stream.common.sql;

import io.emqx.stream.common.Constants;
import net.sf.jsqlparser.schema.Column;

import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public final class SqlFunctionProvider {
  private static Map<String, SqlFunction> functions;

  public static Map<String, SqlFunction> getAllFunctions(){
    if(functions == null){
      functions = new HashMap<>();
      functions.put("count", new SqlFunction().name("count").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Collections.singletonList(Column.class))).returnType(Long.class)
              .description("Count the number of final result"));
      functions.put("lag", new SqlFunction().name("lag").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Collections.singletonList(Column.class))).returnType(Object.class)
              .description("The last row of current query"));
      functions.put("size", new SqlFunction().name("size").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.emptyList()).returnType(Long.class)
              .description("The number of records in the current window regardless the record passes the filter or not"));
      functions.put("getmetadatapropertyvalue", new SqlFunction().name("getmetadatapropertyvalue").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, String.class))).returnType(Object.class)
              .description("Get a meta data of a table"));
      functions.put("ftoc", new SqlFunction().name("ftoc").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Collections.singletonList(Double.class))).returnType(Double.class)
              .description("Convert from farenheit to celcius"));
      functions.put("ctof", new SqlFunction().name("ctof").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Collections.singletonList(Double.class))).returnType(Double.class)
              .description("Convert from celcius to farenheit"));
      functions.put("incircle", new SqlFunction().name("incircle").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Arrays.asList(Double.class, Double.class, Double.class, Double.class, Double.class))).returnType(Boolean.class)
              .description("Check if a location is in Geo circle"));
      functions.put("inpolygon", new SqlFunction().name("inpolygon").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Arrays.asList(Double.class, Double.class, String.class))).returnType(Boolean.class)
              .description("Check if a location is in Geo polygon"));
      functions.put("unnest", new SqlFunction().name("unnest").stages(Collections.unmodifiableList(Collections.singletonList(
              Constants.ValidateStage.SELECT)))
              .arguments(Collections.unmodifiableList(Collections.singletonList(Array.class))).returnType(Object.class)
              .description("Unnest an array into multiple records"));
      functions.put(Constants.TUMBLINGWINDOW, new SqlFunction().name(Constants.TUMBLINGWINDOW).stages(Collections.unmodifiableList(Collections.singletonList(
              Constants.ValidateStage.GROUPBY)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, Long.class))).returnType(Void.class)
              .description("Setup the tumble window"));
      functions.put(Constants.HOPPINGWINDOW, new SqlFunction().name(Constants.HOPPINGWINDOW).stages(Collections.unmodifiableList(Collections.singletonList(
              Constants.ValidateStage.GROUPBY)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, Long.class, Long.class))).returnType(Void.class)
              .description("Setup the hopping window"));
      functions.put(Constants.SLIDINGWINDOW, new SqlFunction().name(Constants.SLIDINGWINDOW).stages(Collections.unmodifiableList(Collections.singletonList(
              Constants.ValidateStage.GROUPBY)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, Long.class))).returnType(Void.class)
              .description("Setup the sliding window"));
      functions.put(Constants.SESSIONWINDOW, new SqlFunction().name(Constants.SESSIONWINDOW).stages(Collections.unmodifiableList(Collections.singletonList(
              Constants.ValidateStage.GROUPBY)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, Long.class, Long.class))).returnType(Void.class)
              .description("Setup the session window"));
      functions.put("split_part", new SqlFunction().name("split_part").stages(Collections.unmodifiableList(Arrays.asList(
              Constants.ValidateStage.SELECT, Constants.ValidateStage.WHERE, Constants.ValidateStage.HAVING)))
              .arguments(Collections.unmodifiableList(Arrays.asList(String.class, String.class, Long.class))).returnType(String.class)
              .description("Split a string and get part of it"));
    }
    return functions;
  }
}
