-- ========================================
-- Migration: Add Intermediate & Advanced Features
-- Date: 2025-12-21
-- Description: Add priorities, tags, due dates, reminders, recurring tasks
-- ========================================

-- Add new columns to tasks table
ALTER TABLE tasks
  -- Intermediate Features: Priorities
  ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM',

  -- Intermediate Features: Tags
  ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::jsonb,

  -- Advanced Features: Due Dates & Reminders
  ADD COLUMN IF NOT EXISTS due_date TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMPTZ,

  -- Advanced Features: Recurring Tasks
  ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20) NOT NULL DEFAULT 'none',
  ADD COLUMN IF NOT EXISTS last_completed_at TIMESTAMPTZ;

-- Add constraints
ALTER TABLE tasks
  ADD CONSTRAINT IF NOT EXISTS chk_priority_values
    CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW'));

ALTER TABLE tasks
  ADD CONSTRAINT IF NOT EXISTS chk_recurrence_values
    CHECK (recurrence_pattern IN ('none', 'daily', 'weekly', 'monthly'));

ALTER TABLE tasks
  ADD CONSTRAINT IF NOT EXISTS chk_reminder_before_due
    CHECK (reminder_time IS NULL OR due_date IS NULL OR reminder_time < due_date);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_tasks_reminder_time ON tasks(reminder_time) WHERE completed = FALSE;

-- Partial index for overdue tasks (query optimization)
CREATE INDEX IF NOT EXISTS idx_overdue_tasks ON tasks(due_date)
  WHERE completed = FALSE AND due_date < NOW();

-- Update existing tasks (backward compatibility)
UPDATE tasks SET priority = 'MEDIUM' WHERE priority IS NULL;
UPDATE tasks SET tags = '[]'::jsonb WHERE tags IS NULL;
UPDATE tasks SET recurrence_pattern = 'none' WHERE recurrence_pattern IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN tasks.priority IS 'Task priority: HIGH, MEDIUM, or LOW (default)';
COMMENT ON COLUMN tasks.tags IS 'Array of user-defined tags (max 10, each max 30 chars)';
COMMENT ON COLUMN tasks.due_date IS 'When task must be completed (timezone-aware)';
COMMENT ON COLUMN tasks.reminder_time IS 'When to send notification (must be before due_date)';
COMMENT ON COLUMN tasks.recurrence_pattern IS 'Recurring pattern: none, daily, weekly, monthly';
COMMENT ON COLUMN tasks.last_completed_at IS 'Last completion time for recurring tasks';
