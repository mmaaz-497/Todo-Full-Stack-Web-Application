-- Audit Service Database Schema
-- Stores all events from all topics for compliance and debugging

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL UNIQUE,
    user_id INTEGER,
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    event_data JSONB NOT NULL,
    source_service VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action_timestamp
    ON audit_logs(user_id, action_type, timestamp DESC);

-- JSONB index for querying event data
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_data_gin ON audit_logs USING GIN(event_data);

-- Comments for documentation
COMMENT ON TABLE audit_logs IS 'Audit log of all system events for compliance and debugging';
COMMENT ON COLUMN audit_logs.event_id IS 'Unique event identifier (UUID from source event)';
COMMENT ON COLUMN audit_logs.action_type IS 'Type of action: task.created, task.updated, task.deleted, task.completed, reminder.due';
COMMENT ON COLUMN audit_logs.resource_type IS 'Type of resource: task, user, reminder';
COMMENT ON COLUMN audit_logs.event_data IS 'Full event payload as JSONB for querying';
COMMENT ON COLUMN audit_logs.source_service IS 'Service that generated the event: api-service, recurring-task-service, etc.';
