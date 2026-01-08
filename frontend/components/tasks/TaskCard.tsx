'use client';

import React from 'react';
import { Task } from '@/lib/api';

interface TaskCardProps {
  task: Task;
  isRemoving?: boolean;
  animationDelay?: number;
  onToggleComplete: (taskId: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
}

/**
 * TaskCard Component
 *
 * Displays a task with all features:
 * - Basic: title, description, completion status
 * - Intermediate: priority badge, tags
 * - Advanced: due date, overdue indicator, recurrence icon
 */
export default function TaskCard({
  task,
  isRemoving = false,
  animationDelay = 0,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskCardProps) {
  // Helper function to parse datetime strings as Pakistan local time
  const parseLocalDate = (dateString: string | null): Date | null => {
    if (!dateString) return null;
    const trimmed = dateString.trim();
    const [datePart, timePart] = trimmed.split('T');
    if (!datePart || !timePart) return null;

    const [year, month, day] = datePart.split('-').map(Number);
    const [hours, minutes, seconds] = timePart.split(':').map(Number);

    // Create date in local time - database stores Pakistan time, display as-is
    return new Date(year, month - 1, day, hours, minutes || 0, seconds || 0);
  };

  const isOverdue = task.is_overdue;
  const dueDate = parseLocalDate(task.due_date);
  const isRecurring = task.recurrence_pattern !== 'none';

  // Priority colors
  const priorityColors = {
    HIGH: 'bg-red-100 text-red-800 border-red-300',
    MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    LOW: 'bg-blue-100 text-blue-800 border-blue-300',
  };

  return (
    <div
      className={`group bg-white rounded-lg p-4 border border-neutral-200 hover:border-neutral-300 shadow-sm hover:shadow-md transition-all duration-200 animate-slideDown ${
        task.completed ? 'opacity-60' : ''
      } ${isRemoving ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'} ${
        isOverdue && !task.completed ? 'border-l-4 border-l-red-500' : ''
      }`}
      style={{ animationDelay: `${animationDelay}ms`, animationFillMode: 'backwards' }}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <label className="flex-shrink-0 mt-0.5 cursor-pointer">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => onToggleComplete(task.id)}
            className="sr-only peer"
          />
          <div className="w-6 h-6 bg-white border-2 border-neutral-400 peer-checked:bg-primary-600 peer-checked:border-primary-600 rounded-full transition-all duration-300 flex items-center justify-center">
            <svg
              className={`w-4 h-4 text-white transition-all duration-300 ${
                task.completed ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
              }`}
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
            </svg>
          </div>
        </label>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <div className="flex items-start gap-2 mb-1">
            <h3
              className={`flex-1 text-lg font-medium text-neutral-900 relative ${
                task.completed ? 'text-neutral-400' : ''
              }`}
            >
              <span
                className={`relative after:absolute after:left-0 after:top-1/2 after:h-0.5 after:bg-neutral-900 after:transition-all after:duration-500 ${
                  task.completed ? 'after:w-full' : 'after:w-0'
                }`}
              >
                {task.title}
              </span>
            </h3>

            {/* Recurring Icon */}
            {isRecurring && (
              <span
                className="flex-shrink-0 text-indigo-600"
                title={`Repeats ${task.recurrence_pattern}`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </span>
            )}
          </div>

          {/* Priority Badge */}
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${
                priorityColors[task.priority]
              }`}
            >
              {task.priority}
            </span>

            {/* Overdue Badge */}
            {isOverdue && !task.completed && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-500 text-white">
                OVERDUE
              </span>
            )}
          </div>

          {/* Description */}
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? 'text-neutral-400' : 'text-neutral-600'
              }`}
            >
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Metadata */}
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-500">
            <span>
              Created {parseLocalDate(task.created_at)?.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })}
            </span>

            {dueDate && (
              <span className={isOverdue && !task.completed ? 'text-red-600 font-medium' : ''}>
                Due {dueDate.toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </span>
            )}

            {task.reminder_time && (
              <span>
                Reminder {parseLocalDate(task.reminder_time)?.toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => onEdit(task)}
            className="p-2 rounded-lg text-neutral-500 hover:text-primary-600 hover:bg-primary-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-200"
            title="Edit"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>

          <button
            onClick={() => onDelete(task.id)}
            className="p-2 rounded-lg text-neutral-500 hover:text-error-600 hover:bg-error-50 transition-colors focus:outline-none focus:ring-2 focus:ring-error-200"
            title="Delete"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
