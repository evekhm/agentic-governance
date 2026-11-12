-- Reconstructs end-to-end chain of custody (User -> Agent Turn -> MCP Tool -> Database SQL)
-- Mirrors Snippet 21 in ep01_securing_agent_to_database.html.
WITH agent_tool_turns AS (
  SELECT
    trace_id,
    invocation_id,
    session_id,
    user_id,
    agent_name,
    JSON_VALUE(content, '$.tool_name') AS mcp_tool_name,
    JSON_VALUE(content, '$.tool_provenance') AS tool_provenance,
    timestamp AS tool_timestamp
  FROM `${GOV_PROJECT_ID}.security_telemetry.agent_events`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    AND event_type = 'TOOL_STARTING'
),
db_data_access AS (
  SELECT
    REGEXP_EXTRACT(protopayload_auditlog.requestMetadata.callerSuppliedUserAgent,
                   r"traceparent='00-([a-f0-9]{32})-") AS trace_id,
    protopayload_auditlog.authenticationInfo.principalEmail AS db_principal,
    protopayload_auditlog.methodName AS db_method,
    JSON_VALUE(protopayload_auditlog.requestJson, '$.query') AS executed_sql,
    timestamp AS db_timestamp
  FROM `${GOV_PROJECT_ID}.security_telemetry.cloudaudit_googleapis_com_data_access`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
)
SELECT
  a.tool_timestamp,
  a.user_id AS verified_human_caller,
  a.agent_name,
  a.mcp_tool_name,
  a.tool_provenance,
  d.db_principal,
  d.executed_sql,
  a.trace_id
FROM agent_tool_turns AS a
INNER JOIN db_data_access AS d
  USING (trace_id)
ORDER BY a.tool_timestamp DESC;
