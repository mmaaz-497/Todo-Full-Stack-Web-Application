'use client';

import React from 'react';
import { TaskPriority } from '@/lib/api';

interface PrioritySelectorProps {
  value: TaskPriority;
  onChange: (priority: TaskPriority) => void;
  className?: string;
}

const PRIORITY_OPTIONS: { value: TaskPriority; label: string; color: string }[] = [
  { value: 'HIGH', label: 'High', color: 'bg-red-500 hover:bg-red-600 text-white' },
  { value: 'MEDIUM', label: 'Medium', color: 'bg-yellow-500 hover:bg-yellow-600 text-white' },
  { value: 'LOW', label: 'Low', color: 'bg-blue-500 hover:bg-blue-600 text-white' },
];

/**
 * PrioritySelector Component
 *
 * Intermediate Feature: 3-button priority picker with color coding
 * - HIGH (Red)
 * - MEDIUM (Yellow)
 * - LOW (Blue)
 */
export default function PrioritySelector({ value, onChange, className = '' }: PrioritySelectorProps) {
  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <label className="text-sm font-medium text-gray-700">Priority</label>
      <div className="flex gap-2">
        {PRIORITY_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`
              flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200
              ${
                value === option.value
                  ? `${option.color} ring-2 ring-offset-2 ring-gray-400`
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
              }
            `}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
