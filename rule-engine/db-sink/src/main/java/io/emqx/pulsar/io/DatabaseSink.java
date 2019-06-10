package io.emqx.pulsar.io;

import io.emqx.pulsar.io.jdbc.JdbcAbstractSink;
import io.emqx.pulsar.io.jdbc.JdbcUtils;
import io.emqx.stream.common.JsonParser;
import lombok.extern.slf4j.Slf4j;
import org.apache.pulsar.functions.api.Record;

import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.text.DecimalFormat;
import java.util.Map;

@SuppressWarnings("unused")
@Slf4j
public class DatabaseSink extends JdbcAbstractSink<String> {


    @SuppressWarnings("unused")
    @Override
    public void bindValue(PreparedStatement insertStatement, Record<String> message) throws Exception {
        log.debug("Receive message :{}", message.getValue());
        int index = 1;
        Map<String, Object> actionMessage = JsonParser.parseMqttMessage(message.getValue());

        if (actionMessage != null) {
            //noinspection unchecked
            Map<String, Object> action = (Map<String, Object>) actionMessage.get("action");
            DatabaseActionConfig dbActionConfig = DatabaseActionConfig.load(action);
            Map<String, String> columnMap = dbActionConfig.getColumns();
            //noinspection unchecked
            Map<String, Object> value = (Map<String, Object>) actionMessage.get("value");
            for (JdbcUtils.ColumnId columnId : tableDefinition.getColumns()) {
                String colName = columnId.getName();
                if (getColumnList().contains(colName)) {
                    String field = columnMap.get(colName);
                    Object obj = null;
                    if (field != null) {
                        obj = value.get(field);
                    }
                    setColumnValue(insertStatement, index++, obj, columnId.getType());
                }
            }

            log.debug("Insert sql is {}", insertStatement.toString());

        }


    }

    private static void setColumnValue(PreparedStatement statement, int index, Object value, int type) throws Exception {
//        timestamp
        if (type == 93 && value != null) {
            DecimalFormat decimalFormat = new DecimalFormat("0");
            long time = Long.valueOf(decimalFormat.format(value));
            statement.setTimestamp(index, new Timestamp(time));
        } else if (value instanceof Integer) {
            statement.setInt(index, (Integer) value);
        } else if (value instanceof Long) {
            statement.setLong(index, (Long) value);
        } else if (value instanceof Double) {
            statement.setDouble(index, (Double) value);
        } else if (value instanceof Float) {
            statement.setFloat(index, (Float) value);
        } else if (value instanceof Boolean) {
            statement.setBoolean(index, (Boolean) value);
        } else if (value instanceof String) {
            statement.setString(index, (String) value);
        } else if (value instanceof Short) {
            statement.setShort(index, (Short) value);
        } else if (value == null) {
            statement.setNull(index, type);
        } else if (value instanceof Map) {
            String valueStr = JsonParser.toJson(value);
            statement.setString(index, valueStr);
        } else {
            throw new Exception("Not support value type, need to add it. " + value.getClass());
        }
    }


}

