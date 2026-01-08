'use client';

import React from 'react';
import { RecurrencePattern } from '@/lib/api';

interface RecurrenceSelectorProps {
  value: RecurrencePattern;
  onChange: (pattern: RecurrencePattern) => void;
  className?: string;
}

const RECURRENCE_OPTIONS: { value: RecurrencePattern; label: string; description: string }[] = [
  { value: 'none', label: 'None', description: 'One-time task' },
  { value: 'daily', label: 'Daily', description: 'Repeats every day' },
  { value: 'weekly', label: 'Weekly', description: 'Repeats every week' },
  { value: 'monthly', label: 'Monthly', description: 'Repeats every month' },
];

/**
 * RecurrenceSelector Component
 *
 * Advanced Feature: Dropdown for selecting recurring task pattern
 * - none (default)
 * - daily
 * - weekly
 * - monthly
 */
export default function RecurrenceSelector({ value, onChange, className = '' }: RecurrenceSelectorProps) {
  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <label className="text-sm font-medium text-gray-700">Repeat</label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value as RecurrencePattern)}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
      >
        {RECURRENCE_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} - {option.description}
          </option>
        ))}
      </select>

      {value !== 'none' && (
        <p className="text-xs text-gray-500">
          A new task will be created automatically when you mark this task as complete.
        </p>
      )}
    </div>
  );
}
