-- Phase V Database Migration: Add Advanced Features
-- Migration: 003_add_phase_v_fields.sql
-- Purpose: Extend tasks table with recurring tasks, reminders, priority, tags, and search features
-- Date: 2026-01-02

-- Add priority column with constraint
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

-- Add tags column as PostgreSQL array
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';

-- Add due_date column with timezone support
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;

-- Add reminder_offset column (ISO 8601 duration)
ALTER TABLE tasks ADD COLUMN reminder_offset INTERVAL;

-- Add recurrence_rule column as JSONB for flexible recurrence patterns
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;

-- Add parent_task_id for linking recurring task occurrences
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE;

-- Create indexes for performance optimization
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);  -- GIN index for array containment queries
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id);

-- Create recurring_task_state table for tracking occurrence generation
CREATE TABLE recurring_task_state (
  task_id INTEGER PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  last_generated_at TIMESTAMPTZ NOT NULL,
  next_occurrence_due TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create audit_logs table for compliance and debugging
CREATE TABLE audit_logs (
  log_id BIGSERIAL PRIMARY KEY,
  event_id UUID NOT NULL,
  user_id INTEGER,
  action_type VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id INTEGER,
  payload JSONB NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  source_service VARCHAR(100) NOT NULL
);

-- Create indexes for audit_logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Add comment documentation
COMMENT ON COLUMN tasks.priority IS 'Task priority level: low, medium, high, urgent';
COMMENT ON COLUMN tasks.tags IS 'User-defined tags for categorization';
COMMENT ON COLUMN tasks.due_date IS 'Task deadline with timezone';
COMMENT ON COLUMN tasks.reminder_offset IS 'Time before due_date to send reminder (e.g., 1 hour, 1 day)';
COMMENT ON COLUMN tasks.recurrence_rule IS 'JSONB recurrence pattern: {frequency, interval, days_of_week, day_of_month, end_date}';
COMMENT ON COLUMN tasks.parent_task_id IS 'Links recurring task occurrences to original parent task';
COMMENT ON TABLE recurring_task_state IS 'Tracks last generated occurrence for recurring tasks';
COMMENT ON TABLE audit_logs IS 'Audit trail for all system events (90-day retention)';
