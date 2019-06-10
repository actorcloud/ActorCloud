package io.emqx.pulsar.io.jdbc;

import static com.google.common.base.Preconditions.checkState;

import com.google.common.collect.Lists;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.IntStream;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("WeakerAccess")
public class JdbcUtils {
    @Data(staticConstructor = "of")
    @Setter
    @Getter
    @EqualsAndHashCode
    @ToString
    public static class TableId {
        private final String catalogName;
        private final String schemaName;
        private final String tableName;
    }

    @Data(staticConstructor = "of")
    @Setter
    @Getter
    @EqualsAndHashCode
    @ToString
    public static class ColumnId {
        private final TableId tableId;
        private final String name;
        // SQL type from java.sql.Types
        private final int type;
        private final String typeName;
        // column position in table
        private final int position;
    }

    @Data(staticConstructor = "of")
    @Setter
    @Getter
    @EqualsAndHashCode
    @ToString
    public static class TableDefinition {
        private final TableId tableId;
        private final List<ColumnId> columns;
    }

    private static final Logger log = LoggerFactory.getLogger(JdbcUtils.class);

    public JdbcUtils() {
    }

    /**
     * Given a driver type(such as mysql), return its jdbc driver class name.
     * TODO: test and support more types, also add Driver in pom file.
     */
    public static String getDriverClassName(String driver) throws Exception {
        if (driver.equals("mysql")) {
            return "com.mysql.jdbc.Driver";
        }
        if (driver.equals("sqlite")) {
            return "org.sqlite.JDBC";
        }
        if (driver.equals("postgresql")) {
            return "org.postgresql.Driver";
        } else {
            throw new Exception("Not tested jdbc driver type: " + driver);
        }
    }

    /**
     * Get the {@link Connection} for the given jdbcUrl.
     */
    public static Connection getConnection(String jdbcUrl, Properties properties) throws Exception {
        String driver = jdbcUrl.split(":")[1];
        String driverClassName = getDriverClassName(driver);
        Class.forName(driverClassName);

        return DriverManager.getConnection(jdbcUrl, properties);
    }

    /**
     * Get the {@link TableId} for the given tableName.
     */
    public static TableId getTableId(Connection connection, String tableName) throws Exception {
        DatabaseMetaData metadata = connection.getMetaData();
        try (ResultSet rs = metadata.getTables(null, null, tableName, new String[]{"TABLE"})) {
            if (rs.next()) {
                String catalogName = rs.getString(1);
                String schemaName = rs.getString(2);
                String gotTableName = rs.getString(3);
                checkState(tableName.equals(gotTableName),
                        "TableName not match: " + tableName + " Got: " + gotTableName);
                if (log.isDebugEnabled()) {
                    log.debug("Get Table: {}, {}, {}", catalogName, schemaName, tableName);
                }
                return TableId.of(catalogName, schemaName, tableName);
            } else {
                throw new Exception("Not able to find table: " + tableName);
            }
        }
    }

    /**
     * Get the {@link TableDefinition} for the given table.
     */
    public static TableDefinition getTableDefinition(Connection connection, TableId tableId) throws Exception {
        TableDefinition table = TableDefinition.of(tableId, Lists.newArrayList());

        try (ResultSet rs = connection.getMetaData().getColumns(
                tableId.getCatalogName(),
                tableId.getSchemaName(),
                tableId.getTableName(),
                null
        )) {
            while (rs.next()) {
                final String columnName = rs.getString(4);

                final int sqlDataType = rs.getInt(5);
                final String typeName = rs.getString(6);
                final int position = rs.getInt(17);
                table.columns.add(ColumnId.of(tableId, columnName, sqlDataType, typeName, position));
                if (log.isDebugEnabled()) {
                    log.debug("Get column. name: {}, data type: {}, position: {}", columnName, typeName, position);
                }
            }
            return table;
        }
    }

    @SuppressWarnings("unused")
    public static String buildInsertSql(TableDefinition table) {
        StringBuilder builder = new StringBuilder();
        builder.append("INSERT INTO ");
        builder.append(table.tableId.getTableName());
        builder.append("(");

        table.columns.forEach(columnId -> {
            String colName = columnId.name;
            //  包含大写字母需要特殊处理
            if (isContainUpper(colName)) {
                builder.append("\"").append(columnId.getName()).append("\"").append(",");
            } else {
                builder.append(columnId.getName()).append(",");
            }
        });
        builder.deleteCharAt(builder.length() - 1);

        builder.append(") VALUES(");
        IntStream.range(0, table.columns.size() - 1).forEach(i -> builder.append("?,"));
        builder.append("?)");

        return builder.toString();
    }

    /**
     * Build insert sql with specified columns
     *
     * @param table      {@link TableDefinition}
     * @param columnList column list
     * @return insert sql
     */
    public static String buildColumnSql(TableDefinition table, List<String> columnList) {
        StringBuilder builder = new StringBuilder();
        builder.append("INSERT INTO ");
        builder.append(table.tableId.getTableName());
        builder.append("(");

        AtomicInteger columnCount = new AtomicInteger();
        table.columns.forEach(columnId -> {
            String colName = columnId.name;
            if (columnList.contains(colName)) {
                //  包含大写字母需要特殊处理
                if (isContainUpper(colName)) {
                    builder.append("\"").append(columnId.getName()).append("\"").append(",");
                } else {
                    builder.append(columnId.getName()).append(",");
                }
                columnCount.addAndGet(1);
            }

        });
        builder.deleteCharAt(builder.length() - 1);

        builder.append(") VALUES(");
        IntStream.range(0, columnCount.get() - 1).forEach(i -> builder.append("?,"));
        builder.append("?)");
        return builder.toString();
    }

    public static PreparedStatement buildInsertStatement(Connection connection, String insertSQL) throws SQLException {
        return connection.prepareStatement(insertSQL);
    }

    public static boolean isContainUpper(String str) {
        String regex = ".*[A-Z]+.*";
        Matcher m = Pattern.compile(regex).matcher(str);
        return m.matches();
    }


}
