package io.emqx.stream.common.internal;

import org.slf4j.Logger;
import org.slf4j.Marker;

public class MockLogger implements Logger {

  @Override
  public String getName() {

    return null;
  }

  @Override
  public boolean isTraceEnabled() {

    return false;
  }

  @Override
  public void trace(String msg) {


  }

  @Override
  public void trace(String format, Object arg) {


  }

  @Override
  public void trace(String format, Object arg1, Object arg2) {


  }

  @Override
  public void trace(String format, Object... arguments) {


  }

  @Override
  public void trace(String msg, Throwable t) {


  }

  @Override
  public boolean isTraceEnabled(Marker marker) {

    return false;
  }

  @Override
  public void trace(Marker marker, String msg) {


  }

  @Override
  public void trace(Marker marker, String format, Object arg) {


  }

  @Override
  public void trace(Marker marker, String format, Object arg1, Object arg2) {


  }

  @Override
  public void trace(Marker marker, String format, Object... argArray) {


  }

  @Override
  public void trace(Marker marker, String msg, Throwable t) {


  }

  @Override
  public boolean isDebugEnabled() {

    return false;
  }

  @Override
  public void debug(String msg) {
    this.info(msg);
  }

  @Override
  public void debug(String format, Object arg) {
    this.info(format, arg);
  }

  @Override
  public void debug(String format, Object arg1, Object arg2) {
    this.info(format, arg1, arg2);
  }

  @Override
  public void debug(String format, Object... arguments) {
    this.info(format, arguments);
  }

  @Override
  public void debug(String msg, Throwable t) {
    this.info(msg);
    t.printStackTrace();
  }

  @Override
  public boolean isDebugEnabled(Marker marker) {

    return false;
  }

  @Override
  public void debug(Marker marker, String msg) {


  }

  @Override
  public void debug(Marker marker, String format, Object arg) {


  }

  @Override
  public void debug(Marker marker, String format, Object arg1, Object arg2) {


  }

  @Override
  public void debug(Marker marker, String format, Object... arguments) {


  }

  @Override
  public void debug(Marker marker, String msg, Throwable t) {


  }

  @Override
  public boolean isInfoEnabled() {

    return false;
  }

  @Override
  public void info(String msg) {
    System.out.println(msg);
  }

  @Override
  public void info(String format, Object arg) {
    this.info(format + arg);
  }

  @Override
  public void info(String format, Object arg1, Object arg2) {
    this.info(format + arg1 + arg2);
  }

  @Override
  public void info(String format, Object... arguments) {
    this.info(format);
  }

  @Override
  public void info(String msg, Throwable t) {
    this.info(msg);
  }

  @Override
  public boolean isInfoEnabled(Marker marker) {

    return false;
  }

  @Override
  public void info(Marker marker, String msg) {


  }

  @Override
  public void info(Marker marker, String format, Object arg) {


  }

  @Override
  public void info(Marker marker, String format, Object arg1, Object arg2) {


  }

  @Override
  public void info(Marker marker, String format, Object... arguments) {


  }

  @Override
  public void info(Marker marker, String msg, Throwable t) {


  }

  @Override
  public boolean isWarnEnabled() {

    return false;
  }

  @Override
  public void warn(String msg) {


  }

  @Override
  public void warn(String format, Object arg) {


  }

  @Override
  public void warn(String format, Object... arguments) {


  }

  @Override
  public void warn(String format, Object arg1, Object arg2) {


  }

  @Override
  public void warn(String msg, Throwable t) {


  }

  @Override
  public boolean isWarnEnabled(Marker marker) {

    return false;
  }

  @Override
  public void warn(Marker marker, String msg) {


  }

  @Override
  public void warn(Marker marker, String format, Object arg) {


  }

  @Override
  public void warn(Marker marker, String format, Object arg1, Object arg2) {


  }

  @Override
  public void warn(Marker marker, String format, Object... arguments) {


  }

  @Override
  public void warn(Marker marker, String msg, Throwable t) {


  }

  @Override
  public boolean isErrorEnabled() {

    return false;
  }

  @Override
  public void error(String msg) {


  }

  @Override
  public void error(String format, Object arg) {


  }

  @Override
  public void error(String format, Object arg1, Object arg2) {


  }

  @Override
  public void error(String format, Object... arguments) {


  }

  @Override
  public void error(String msg, Throwable t) {


  }

  @Override
  public boolean isErrorEnabled(Marker marker) {

    return false;
  }

  @Override
  public void error(Marker marker, String msg) {


  }

  @Override
  public void error(Marker marker, String format, Object arg) {


  }

  @Override
  public void error(Marker marker, String format, Object arg1, Object arg2) {


  }

  @Override
  public void error(Marker marker, String format, Object... arguments) {


  }

  @Override
  public void error(Marker marker, String msg, Throwable t) {


  }

}
