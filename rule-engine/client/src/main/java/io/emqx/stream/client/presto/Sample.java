package io.emqx.stream.client.presto;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;

public class Sample {
  // JDBC driver name and database URL
  static final String JDBC_DRIVER = "com.facebook.presto.jdbc.PrestoDriver";  
  static final String DB_URL = "jdbc:presto://192.168.0.2:8081/pulsar/";

  //  Database credentials
  static final String USER = "username";
  static final String PASS = null;
  
  public static void main(String[] args) {
    Connection conn = null;
    Statement stmt = null;
    try{
      //STEP 2: Register JDBC driver
      Class.forName(JDBC_DRIVER);

      //STEP 3: Open a connection
      System.out.println("Connecting to database...");
      conn = DriverManager.getConnection(DB_URL,USER,PASS);

      //STEP 4: Execute a query
      System.out.println("Creating statement...");
      stmt = conn.createStatement();
      String sql;
      sql = "SELECT * FROM \"public/default\".test_topic limit 1";
      ResultSet rs = stmt.executeQuery(sql);

      //STEP 5: Extract data from result set
      //while(rs.next()){
          // //Retrieve by column name
          // int field1  = rs.getInt("field1");
          // String field2 = rs.getString("field2");
          // long field3 = rs.getLong("field3");

          // //Display values
          // System.out.print("field1: " + field1);
          // System.out.print(", field2: " + field2);
          // System.out.print(", field3: " + field3);
          Map<String, Object> result = resultSetToMap(rs);
          System.out.print(result.get("field1"));
      //}
      //STEP 6: Clean-up environment
      rs.close();
      stmt.close();
      conn.close();
    } catch(Exception se){
      //Handle errors for JDBC
      se.printStackTrace();
    }//Handle errors for Class.forName
    finally{
      //finally block used to close resources
      try{
          if(stmt!=null)
            stmt.close();
      }catch(SQLException ignored){
      }// nothing we can do
      try{
          if(conn!=null)
            conn.close();
      }catch(SQLException se){
          se.printStackTrace();
      }//end finally try
    }//end try
    System.out.println("Goodbye!");
  }

  private static Map<String, Object> resultSetToMap(ResultSet rs) throws SQLException {
    ResultSetMetaData md = rs.getMetaData();
    int columns = md.getColumnCount();
    Map<String, Object> result = null;
    if(rs.next()){
      System.out.println("got resultset of " + columns + " columns");
      result = new HashMap<>(columns - 7);
      for(int i=1;i<=columns;i++){
        String colName = md.getColumnName(i);
        if(colName.startsWith("__") && colName.endsWith("__")){
          continue;
        }
        result.put(md.getColumnName(i), rs.getObject(i));
      }
    }
    return result;
  }
}