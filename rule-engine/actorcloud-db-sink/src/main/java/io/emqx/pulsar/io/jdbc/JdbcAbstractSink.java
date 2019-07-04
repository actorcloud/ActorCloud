package io.emqx.pulsar.io.jdbc;

import com.google.common.collect.Lists;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.io.core.Sink;
import org.apache.pulsar.io.core.SinkContext;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * A Simple abstract class for Jdbc sink
 * Users need to implement extractKeyValue function to use this sink
 */
@Slf4j
public abstract class JdbcAbstractSink<T> implements Sink<T> {
    @Getter
    private Connection connection;
    private String jdbcUrl;

    // for flush
    private List<Record<T>> incomingList;
    private List<Record<T>> swapList;
    private AtomicBoolean isFlushing;
    private PreparedStatement insertStatement;

    protected JdbcUtils.TableDefinition tableDefinition;
    private int batchSize;
    private ScheduledExecutorService flushExecutor;
    @Getter
    private List<String> columnList;

    @Override
    public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {
        // ----- Runtime fields
        JdbcSinkConfig jdbcSinkConfig = JdbcSinkConfig.load(config);

        jdbcUrl = jdbcSinkConfig.getJdbcUrl();
        if (jdbcSinkConfig.getJdbcUrl() == null) {
            throw new IllegalArgumentException("Required jdbc Url not set.");
        }

        Properties properties = new Properties();
        String username = jdbcSinkConfig.getUserName();
        String password = jdbcSinkConfig.getPassword();
        if (username != null) {
            properties.setProperty("user", username);
        }
        if (password != null) {
            properties.setProperty("password", password);
        }

        connection = JdbcUtils.getConnection(jdbcUrl, properties);
        connection.setAutoCommit(false);
        log.info("Opened jdbc connection: {}, autoCommit: {}", jdbcUrl, connection.getAutoCommit());
        columnList = Arrays.asList(jdbcSinkConfig.getColumns());
        String tableName = jdbcSinkConfig.getTableName();
        JdbcUtils.TableId tableId = JdbcUtils.getTableId(connection, tableName);
        tableDefinition = JdbcUtils.getTableDefinition(connection, tableId);
        insertStatement = JdbcUtils.buildInsertStatement(connection, JdbcUtils.buildColumnSql(tableDefinition, columnList));

        int timeoutMs = jdbcSinkConfig.getTimeoutMs();
        batchSize = jdbcSinkConfig.getBatchSize();
        incomingList = Lists.newArrayList();
        swapList = Lists.newArrayList();
        isFlushing = new AtomicBoolean(false);

        flushExecutor = Executors.newScheduledThreadPool(1);
        flushExecutor.scheduleAtFixedRate(this::flush, timeoutMs, timeoutMs, TimeUnit.MILLISECONDS);

    }

    @Override
    public void close() throws Exception {
        if (!connection.getAutoCommit()) {
            connection.commit();
        }
        flushExecutor.shutdown();
        if (connection != null) {
            connection.close();
        }
        log.info("Closed jdbc connection: {}", jdbcUrl);
    }

    @SuppressWarnings("RedundantThrows")
    @Override
    public void write(Record<T> record) throws Exception {
        int number;
        synchronized (incomingList) {
            incomingList.add(record);
            number = incomingList.size();

        }
        if (number == batchSize) {
            flushExecutor.schedule(this::flush, 0, TimeUnit.MICROSECONDS);
        }

    }

    // bind value with a PreparedStatement
    protected abstract void bindValue(PreparedStatement statement, Record<T> message) throws Exception;


    @SuppressWarnings("unused")
    private void flush() {
        // if not in flushing state, do flush, else return;
        if (incomingList.size() > 0 && isFlushing.compareAndSet(false, true)) {
            if (log.isDebugEnabled()) {
                log.debug("Starting flush, queue size: {}", incomingList.size());
            }
            if (!swapList.isEmpty()) {
                throw new IllegalStateException("swapList should be empty since last flush. swapList.size: " + swapList.size());
            }

            synchronized (incomingList) {
                List<Record<T>> tmpList;
                swapList.clear();

                tmpList = swapList;
                swapList = incomingList;
                incomingList = tmpList;
            }

            int updateCount = 0;
            boolean noInfo = false;
            try {
                // bind each record value
                for (Record<T> record : swapList) {
                    try {
                        bindValue(insertStatement, record);
                    } catch (Exception e) {
                        log.error("Got exception when bindValue ", e);
                        record.fail();
                        continue;
                    }
                    insertStatement.addBatch();
                    record.ack();
                }

                for (int updates : insertStatement.executeBatch()) {
                    if (updates == Statement.SUCCESS_NO_INFO) {
                        continue;
                    }
                    updateCount += 1;
                }
                connection.commit();
                swapList.forEach(Record::ack);
            } catch (SQLException e1) {
                for (Throwable throwable : e1) {
                    log.error("Got SQLException:", throwable);
                }
//                swapList.forEach(Record::fail);
            } catch (Exception e) {
                log.error("Got exception ", e);
//                swapList.forEach(Record::fail);
            }

            if (swapList.size() != updateCount) {
                log.error("Update count {}  not match total number of records {}", updateCount, swapList.size());
            }

            // finish flush
            if (log.isDebugEnabled()) {
                log.debug("Finish flush, queue size: {}", swapList.size());
            }
            swapList.clear();
            isFlushing.set(false);
        } else {
            if (log.isDebugEnabled()) {
                log.debug("Already in flushing state, will not flush, queue size: {}", incomingList.size());
            }
        }
    }

}
