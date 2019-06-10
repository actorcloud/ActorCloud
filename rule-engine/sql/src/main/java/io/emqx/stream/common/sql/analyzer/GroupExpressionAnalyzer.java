package io.emqx.stream.common.sql.analyzer;

import io.emqx.stream.common.Constants;
import io.emqx.stream.common.sql.plan.AggregatePlan;
import io.emqx.stream.common.sql.pojo.Window;
import io.emqx.stream.common.sql.visitor.ExpressionEvaluator;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import net.sf.jsqlparser.expression.Expression;
import net.sf.jsqlparser.expression.ExpressionVisitorAdapter;
import net.sf.jsqlparser.expression.Function;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

@RequiredArgsConstructor
public class GroupExpressionAnalyzer extends ExpressionVisitorAdapter {
  @NonNull
  protected final AggregatePlan aggregatePlan;

  @NonNull
  protected final Iterator<Expression> groupsIterator;

  @Override
  public void visit(Function function) {
    ExpressionEvaluator evaluator = new ExpressionEvaluator();
    String name = function.getName().toLowerCase();
    List<Expression> params = function.getParameters() != null ? function.getParameters().getExpressions() : new ArrayList<>();
    switch(name){
      case Constants.TUMBLINGWINDOW:
        analyzeWindow(evaluator, params, 2, Constants.WindowType.TUMBLING);
      break;
      case Constants.HOPPINGWINDOW:
        analyzeWindow(evaluator, params, 3, Constants.WindowType.HOPPING);
        break;
      case Constants.SLIDINGWINDOW:
        analyzeWindow(evaluator, params, 2, Constants.WindowType.SLIDING);
        break;
      case Constants.SESSIONWINDOW:
        analyzeWindow(evaluator, params, 3, Constants.WindowType.SESSION);
        break;
    }

  }

  private void analyzeWindow(ExpressionEvaluator evaluator, List<Expression> params, int paramSize, Constants.WindowType windowType) {
    //TODO extract function validator
    if (params.size() != paramSize) {
      throw new RuntimeException("Invalid parameters");
    }
    String unit = (String) evaluator.evaluate(params.get(0));
    long windowSize = (long) evaluator.evaluate(params.get(1));
    Window window = new Window().type(windowType).isDuration(isDuration(unit))
      .size(getWindowSize(unit, windowSize));
    if(paramSize == 3){
      long hopSize = (long) evaluator.evaluate(params.get(2));
      window.hopSize(getWindowSize(unit, hopSize));
    }
    aggregatePlan.window(window);
    groupsIterator.remove();
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

}