## Stream Analytic SQL

This project offers a SQL-like query language for performing transformation and computation over streams.

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

### Unit
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

### Group By
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

### Built-in Functions for Stream Analytic
This project provides some built in functions that is calculated based on states.

| Function   | Description            | Syntax
| --------   | -----------------------| -------
| count      | return the number of items in a group | count(expression | *)
| avg     | return the average of the values in a group | avg(expression)
| max     | returns the maximum value in the expression | max(expression)
| min     | returns the maximum value in the expression | min(expression)
| size     | returns the number of items in a group no matter if it pass the condition. Comparing size to count can determine if all items in the group have passed the filter condition | size()
| lag     | return the "previous" item in the stream | lag(expression)


### Join
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
