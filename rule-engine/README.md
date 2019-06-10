[Name] rule engine is a stream based rule processing and managing platform that based on [Pulsar 2.2.0](https://pulsar.apache.org/docs/en/2.2.0/pulsar-2.0/).

# Getting Started
**System requirements**
In order to use rule engine, you'll need to install Java 8, [Pulsar](https://pulsar.apache.org/docs/en/2.2.0/pulsar-2.0/), [EMQX](http://emqtt.com/) 

* Start EMQX and pulsar
* Extract rule engine to the same machine for pulsar broker.
* Take database action as an example. Install database, and modify the configuration file db-sink-config.yml.
* Run CLI to start the rule engine
```$bash
$ stream-admin create all
```
* Create rule through REST API
```http
POST http://localhost:8888/rules/
{
    "id": "ruleSingle",
    "sql": "SELECT temperature FROM firstTopic where temperature > 26.5",
    "enabled": true,
    "actions": [
        {
            "db": {}
        }
    ]
}
```
* Feed data into MQTT topic firstTopic like
```json
{
  "temperature": 28,
  "other" : "none"
}
```
* The temperature data should be saved to the database

# Rule Definition

A rule is composed by the following elements:
```
Rule{
    id*	string, must be unique
        example: d290f1ee-6c54-4b01-90e6-d701748f0851
    sql*	string, the stream SQL
        example: SELECT * from topic
    enabled*	boolean, whether to enable the rule or not
    actions*	list, the actions to invoke when the rule is fulfilled
        example: List [ OrderedMap { "db": OrderedMap { "columns": OrderedMap { "msgTime": "ts", "topic": "topic", "payload": "payload", "deviceID": "device_id", "tenantID": "tenant_id" } } } ]
}
```

## Stream SQL
[NAME] offers a SQL-like query language for performing transformations and computations over streams of events. It is a subset of T-SQL syntax

### Windows

Since stream is unbounded, aggregates on streams are scoped by **windows**. Windows can be _time driven_ (example: every 30 seconds) or _data driven_ (example: every 100 elements). The types of windows supported now are tumbling window, hopping window and sliding window. All types are supported for both time driven and data driven.

In this project, windows are treated as a group.The window function must be used in group by clause. It can be used together with other group clause.

**example**

`SELECT color FROM sample where temperature > 25.0 group by tumblingwindow('ss', 4)`

`SELECT color FROM sample where temperature > 25.0 group by color,tumblingwindow('ss', 4)`

#### Tumbling Window
Tumbling windows are a series of fixed-sized, non-overlapping and contiguous time intervals. The following diagram illustrates a stream with a series of events and how they are mapped into 5-second tumbling windows.

![Stream Analytics tumbling window](https://docs.microsoft.com/en-us/stream-analytics-query/media/tumbling-window-azure-stream-analytics/streamanalytics-tumblingwindow5mins.png)

**Syntax**

`tumblingwindow( unit, windowsize)`

#### Hopping Window
hopping windows model scheduled overlapping windows.

![Stream Analytics hopping window](https://docs.microsoft.com/en-us/stream-analytics-query/media/hopping-window-azure-stream-analytics/streamanalytics-hoppingwindow.png)

**Syntax**

`hoppingwindow(unit, size, hopSize)`

#### Sliding Window
When using a sliding window, the system is asked to logically consider all possible windows of a given length. As the number of such windows would be infinite, Azure Stream Analytics instead outputs events only for those points in time when the content of the window actually changes, in other words when an event entered or exits the window.

![Stream Analytics sliding window](https://docs.microsoft.com/en-us/stream-analytics-query/media/sliding-window-azure-stream-analytics/streamanalytics-slidingwindow.png)

**Syntax**

`slidingwindow(unit, size)`

#### Session Window
When using a sliding window, the system is asked to logically consider all possible windows of a given length. As the number of such windows would be infinite, Azure Stream Analytics instead outputs events only for those points in time when the content of the window actually changes, in other words when an event entered or exits the window.

![Stream Analytics sliding window](https://docs.microsoft.com/en-us/stream-analytics-query/media/session-window-azure-stream-analytics/streamanalytics-sessionwindow.png)

**Syntax**

`sessionwindow(unit, duration, timeout)`

#### Unit
The units supported by window function is not only time unit but also data count. Please check the full list of supported units.

| Unit   | Description
| ----   | -----------------------
| tt     | data elements count
| mc     | microsecond
| ms     | millisecond
| ss     | second
| mi     | minute
| hh     | hour
| dd     | day

### Query Language Elements

#### Select
Retrieves rows from input streams and enables the selection of one or many columns from one or many input streamss. 

```sql
SELECT <select_list>   
<select_list> ::=   
    {   
      *   
      | { input_name |  input_alias }.*   
      | {  
          [ { input_name | input_alias }. ]  
               { column_name }  
     | expression [ [ AS ] column_alias ]  
         }  
      | column_alias = expression   
    } [ ,...n ]  
```
##### Arguments

<b>\*</b>

Specifies that all columns from all input streams in the FROM clause should be returned. The columns are returned by input source, as specified in the FROM clause, and in the order in which they exist in the incoming stream.

<b>input_name | input_alias.*</b>

Limits the scope of the * to the specified input name.

<b>column_name.*</b>

Columns from * expression with names conflicting with previously projected columns in the same SELECT statement are ignored. Columns on the left side of the SELECT statement take precedence over columns on the right.

**column_name**

Is the name of a column to return. Qualify column_name to prevent an ambiguous reference, such as occurs when two input source in the FROM clause have columns with duplicate names.

**expression**

Is a constant, function, any combination of column names, constants, and functions connected by an operator or operators, or a subquery.

**column_alias**

Is an alternative name to replace the column name in the query result set. For example, an alias such as Quantity, or [Quantity to Date], or Qty can be specified for a column named quantity. Aliases are used also to specify names for the results of expressions. column_alias cannot be used in a WHERE, GROUP BY, or HAVING clause.



#### From
Specifies the input stream. The FROM clause is always required for any SELECT statement.

```sql
[ FROM { <input_source> } [ ,...n ] ]  
  
<input_source> ::=   
    {   
      input_name [ [ AS ] table_alias ] 
     | subselect
     | values_list 
    } [ ,...n ]  
```
##### Arguments
<b>input_name</b>

The name of the input stream. Notice that, the input_name does not allow to contain '.' character. If the original mqtt topic has '.', replace it with '$$' in the from clause. `SELECT * from sample$$topic`

**subselect**

A SELECT query, the result will become the input for the current query.

**values list**

A constant list as the input.

#### WHERE
Specifies the search condition for the rows returned by the query.

```sql
[ WHERE <search_condition> ]  
  
<search_condition> ::=   
    { [ NOT ] <predicate> | ( <search_condition> ) }   
    [ { AND | OR } [ NOT ] { <predicate> | ( <search_condition> ) } ]   
[ ,...n ]   
<predicate> ::=   
    { expression { =  | ! = | > | > = | < | < =  } expression  
    | expression [ NOT ] IN (expression, expression, ...n)   }  
```

##### Arguments

**< search_condition >**

Specifies the conditions for the rows returned in the result set for a SELECT statement, query expression, or subquery. There is no limit to the number of predicates that can be included in a search condition.

**NOT**

Negates the Boolean expression specified by the predicate.

**AND**

Combines two conditions and evaluates to TRUE when both of the conditions are TRUE.

**OR**

Combines two conditions and evaluates to TRUE when either condition is TRUE.

**< predicate >**

Is an expression that returns TRUE or FALSE.

**expression**

Is a column name, a constant, a function, a variable, a scalar subquery, or any combination of column names, constants, and functions connected by an operator or operators, or a subquery. The expression can also contain the CASE expression.

**=**

Is the operator used to test the equality between two expressions.

**!=**

Is the operator used to test the condition of two expressions not being equal to each other.

**>**

Is the operator used to test the condition of one expression being greater than the other.

**>=**

Is the operator used to test the condition of one expression being greater than or equal to the other expression.

**<**

Is the operator used to test the condition of one expression being less than the other.

**<=**

Is the operator used to test the condition of one expression being less than or equal to the other expression.

**String_expression**

Is a string of characters.

**[NOT] IN**

Specifies a list of valid values. Use , to separate the values.

#### Group By
Groups a selected set of rows into a set of summary rows by the values of one or more column or expressions.

```sql
GROUP BY <group by spec>  
  
<group by spec> ::=  
    <group by item> [ ,...n ]  
    | <window_type>
  
<group by item> ::=  
    <column_expression>
```

To search aggregate conditions for a group, **HAVING** clause must be used.

```sql
[ HAVING <search condition> ]
```

#### Join
Like standard T-SQL, JOIN in the project are used to combine records from two or more input sources. JOIN in stream are temporal in nature, meaning that each JOIN must provide some limits on how far the matching rows can be separated. The limits can be provided by window and the join will run upon a set of input sources. 

The join syntax can be explicit join or implicit join by specifying multiple _from_ source. _On_ clause will specify the join condition.

```sql
[ FROM { <input_source> } [ ,...n ] ]  
<input_source> ::=   
{  
    input_name [ [ AS ] input_alias ]   
    | <joined_table>   
}  
  
<joined_table> ::=   
{  
    <input_source> <join_type> <input_source> ON <join_condition>   
    | [ <input_source> <join_type> <reference_data> ON <join_condition> ]  
    | [ ( ] <joined_table> [ ) ]   
}  
<join_type> ::=   
    [ { INNER | LEFT | RIGHT | [ OUTER ] } ] JOIN
```

##### Lateral Join
The LATERAL key word can precede a sub-SELECT FROM item. This allows the sub-SELECT to refer to columns of FROM items that appear before it in the FROM list. (Without LATERAL, each sub-SELECT is evaluated independently and so cannot cross-reference any other FROM item.) This is useful to flatten list.

**example**

`SELECT color, c.temp FROM parent as p JOIN LATERAL (SELECT unnest(p.temps) as temp) as c where c.temp > 27.5`

In this example, parent topic has 2 fields color and temps whereas temps is a list of temperatures. The unnest function will flatten the list into multiple records. With LATERAL, these records can be evaluated together with other field, so that each temperature together with its color will be returned as a single row.

##### Record Field Accessor
Unlike standard SQL, the SQL in this project supports to query and access record fields. To access the fields in the record, just seperate it with '$$'.

**example**
Given the message structure is like:
```json
{
  "meta": "metadata",
  "payload" : {
    "temperature":25.3,
    "humidity": 78.3
  }
}
```
To access temperature field of payload, use the below sql

```sql
SELECT payload$$temperature from sampleTopic where payload$$temperature > 25.0
```

### Built-in functions

#### Built-in Functions for Stream Analytic
This project provides some built in functions that is calculated based on states.

| Function   | Description            | Syntax
| --------   | -----------------------| -------
| count      | return the number of items in a group | count(expression | *)
| max     | returns the maximum value in the expression | max(expression)
| min     | returns the maximum value in the expression | min(expression)
| size     | returns the number of items in a group no matter if it pass the condition. Comparing size to count can determine if all items in the group have passed the filter condition | size()
| lag     | return the "previous" item in the stream | lag(expression)

#### Other Built-in Functions
| Function   | Description            | Syntax
| --------   | -----------------------| -------
| getMetaPropertyValue      | return the a property value of the meta data. Currently, only 'topic' property is supported | getMetaPropertyValue(table, string)
| unnest     | flatten the list to multiple rows | unnest(list | expression)
| inCircle     | returns boolean value whether the location is inside a GEO circle | inCircle(latitude, longtitude, centerX, centerY, radius)
| inPolygon     | returns whether the location is inside a GEO polygon | inPolygon(latitude, longtitude, json of points list)
| splitPart     | Split the input string and return the value of an index | splitPart(expression, seperator, index)
| ftoc  | convert from farenheit to celcius | ftoc(double)
| ctof  | convert from celcius to farenheith | ctof(double)

**examples**
```sql
SELECT split_part(getMetadataPropertyValue(input1,'topic'),'/',5) as device_id FROM input1, input2 WHERE input1.timestamp = input2.timestamp

SELECT * FROM mytopic WHERE inCircle(payload$$lat,payload$$lng,39.9,118.38,1968.1)

SELECT * FROM mytopic WHERE inPolygon(payload$$lat,payload$$lng,'[[39.944148,116.391279,],[39.897416,116.35111],[39.896802,116.495135]]')
```

## Actions

# Rest API for rule management

We provide REST API for rule CRUD and start/stop. Please refer to
https://app.swaggerhub.com/apis/ngjaying/rules/1.0.0

# CLI tools

We offer several command-line tools that you can use to manipulate agent, io and existing rules.

```$xslt
Usage: stream-admin create|update <command> <args...>
where command is one of:
    all                 Run all source, sinks and agent.
    source              Run emqx source
    func-distribute     Run the distribute function
    agent               Run the rule agent
    rules               Update all running rules
    sink-db             Run the db sink
    sink-webhook        Run the webhook sink
where argument is one of:
    -force (accepted only with stop command): Decides whether to stop the server forcefully if not stopped by normal shutdown
```

When running create, the entity will be created. If there is already an existing one, it will be deleted and create a new one. When running update, the existing entity will not be deleted, but will just restart.