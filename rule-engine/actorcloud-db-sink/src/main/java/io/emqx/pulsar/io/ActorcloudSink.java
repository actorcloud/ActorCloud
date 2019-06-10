package io.emqx.pulsar.io;

import io.emqx.pulsar.io.jdbc.JdbcAbstractSink;
import io.emqx.pulsar.io.jdbc.JdbcUtils;
import io.emqx.stream.common.Constants;
import io.emqx.stream.common.JsonParser;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import lombok.extern.slf4j.Slf4j;
import org.apache.pulsar.functions.api.Record;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;

@Slf4j
public class ActorcloudSink extends JdbcAbstractSink<String> {
    @Override
    protected void bindValue(PreparedStatement statement, Record<String> message) throws Exception {
        log.info("ActorcloudSink received message: {} ", message.getValue());
        String[] messages = message.getValue().split(Constants.MESSAGE_SEPERATOR);
        if (messages.length != 3) {
            throw new Exception("Invalid message: " + message);
        }
        String topic = messages[0];
        String input = messages[1];
        long ts = Long.parseLong(messages[2]);
        String[] infos = topic.substring(1).split("/", 5);
        if (infos.length != 5) {
            throw new Exception("Invalid topic: " + topic);
        }
        String tenantID = infos[1];
        String deviceID = infos[3];
        String realTopic = infos[4];

        Gson gson = new GsonBuilder()
                .registerTypeAdapter(new TypeToken<Map<String, Object>>() {
                }.getType(), new MapJsonDeserializer())
                .create();
        ActorcloudPayload payload;
        try {
            payload = gson.fromJson(input, ActorcloudPayload.class);
        } catch (JsonSyntaxException e) {
            log.error(e.getMessage());
            throw new Exception("Invalid message: " + input);
        }

        if (payload.isInvalid()) {
            throw new Exception("Invalid message: " + input);
        }
        Map<String, Object> columnMap = new HashMap<>();
        columnMap.put("topic", realTopic);
        columnMap.put("tenantID", tenantID);
        columnMap.put("deviceID", deviceID);
        columnMap.put("msgTime", ts);
        columnMap.put("streamID", payload.getStreamID());
        columnMap.put("dataType", payload.getDataType());
        columnMap.put("data", payload.getDataJson());
        columnMap.put("responseResult", payload.getResultJson());

        if (payload.isGateway() && payload.getSubDevices() != null) {
            for (SubDevice subDevice : payload.getSubDevices()) {
                Map<String, Object> map = new HashMap<>(columnMap);
                map.put("deviceID", subDevice.getDeviceID());
                map.put("data", JsonParser.toJson(subDevice.getData()));
                try {
                    setColumnValue(statement, map);
                    log.debug("Insert sql is {}", statement.toString());
                    statement.addBatch();
                } catch (SQLException e) {
                    throw new Exception("Invalid message: " + input);
                }
            }
        }

        setColumnValue(statement, columnMap);
        log.debug("Insert sql is {}", statement.toString());
    }

    private void setColumnValue(PreparedStatement statement, Map<String, Object> columnMap) throws SQLException {
        int index = 1;
        for (JdbcUtils.ColumnId columnId : tableDefinition.getColumns()) {
            String colName = columnId.getName();
            if (getColumnList().contains(colName)) {
                Object value = columnMap.get(colName);
                if (colName.equals("msgTime")) {
                    statement.setTimestamp(index++, new Timestamp(((long) value)));
                } else if (colName.equals("data") || colName.equals("responseResult")) {
                    statement.setObject(index++, value, columnId.getType());
                } else {
                    if (value == null) {
                        statement.setNull(index++, columnId.getType());
                    } else {
                        if (value instanceof Integer) {
                            statement.setInt(index++, (int) value);
                        } else {
                            statement.setString(index++, ((String) value));
                        }
                    }
                }
            }
        }
    }
}
