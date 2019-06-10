package io.emqx.stream.common.sql.plan;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

@EqualsAndHashCode(callSuper = true)
@Accessors(fluent = true)
@Data
public class SqlPlan extends PlanAdaptor{
}