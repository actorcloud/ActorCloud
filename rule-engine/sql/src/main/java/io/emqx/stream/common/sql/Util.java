package io.emqx.stream.common.sql;

import net.sf.jsqlparser.schema.Table;
import net.sf.jsqlparser.statement.select.FromItem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Util {
  public static String getFromItemName(FromItem fromItem){
    if(fromItem.getAlias() != null){
      return fromItem.getAlias().getName();
    }else if(fromItem instanceof Table){
      return ((Table) fromItem).getName();
    }else{
      return fromItem.toString();
    }
  }

  public static List<Map<String,Object>> deepCopyMapList(List<Map<String,Object>> source){
    List<Map<String,Object>> dest = new ArrayList<>();
    source.forEach(ele -> {
      Map<String, Object> t = new HashMap<>(ele);
      dest.add(t);
    });
    return dest;
  }
}
