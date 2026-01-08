'use client';

import React, { useState } from 'react';
import { TaskCreate, TaskUpdate, TaskPriority, RecurrencePattern } from '@/lib/api';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import PrioritySelector from './PrioritySelector';
import TagInput from './TagInput';
import DateTimePicker from './DateTimePicker';
import RecurrenceSelector from './RecurrenceSelector';

interface TaskFormProps {
  mode: 'create' | 'edit';
  userId: string;
  initialData?: Partial<TaskUpdate>;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

/**
 * TaskForm Component
 *
 * Comprehensive task form supporting all features:
 * - Basic: title, description
 * - Intermediate: priority, tags
 * - Advanced: due date, reminder, recurrence
 */
export default function TaskForm({
  mode,
  userId,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  // Helper to get current time in local format (Pakistan time, no UTC conversion)
  const getCurrentLocalTime = (): string => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
  };

  // Basic fields
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');

  // Intermediate fields
  const [priority, setPriority] = useState<TaskPriority>(
    (initialData?.priority as TaskPriority) || 'MEDIUM'
  );
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);

  // Advanced fields
  const [dueDate, setDueDate] = useState<string | null>(initialData?.due_date || null);
  const [reminderTime, setReminderTime] = useState<string | null>(initialData?.reminder_time || null);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern>(
    (initialData?.recurrence_pattern as RecurrencePattern) || 'none'
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!title.trim()) {
      alert('Title is required');
      return;
    }

    if (reminderTime && dueDate && new Date(reminderTime) >= new Date(dueDate)) {
      alert('Reminder time must be before due date');
      return;
    }

    if (recurrencePattern !== 'none' && !dueDate) {
      alert('Due date is required for recurring tasks');
      return;
    }

    // Build payload
    const payload: TaskCreate | TaskUpdate = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      tags,
      due_date: dueDate || undefined,
      reminder_time: reminderTime || undefined,
      recurrence_pattern: recurrencePattern,
    };

    await onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-xl shadow-lg border-2 border-primary-300"
    >
      <h3 className="text-lg font-semibold mb-4 text-neutral-900">
        {mode === 'create' ? 'Create New Task' : 'Edit Task'}
      </h3>

      <div className="space-y-4">
        {/* Basic Fields */}
        <Input
          label="Title"
          type="text"
          required
          maxLength={200}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
        />

        <div>
          <label className="block mb-2 text-sm font-medium text-neutral-700">
            Description (optional)
          </label>
          <textarea
            maxLength={1000}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2.5 bg-white border-2 border-neutral-300 rounded-lg transition-all duration-200 ease-out focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100 hover:border-neutral-400 text-neutral-900 placeholder:text-neutral-400"
            rows={3}
            placeholder="Add more details..."
          />
        </div>

        {/* Intermediate Fields */}
        <PrioritySelector value={priority} onChange={setPriority} />

        <TagInput value={tags} onChange={setTags} userId={userId} />

        {/* Advanced Fields */}
        <div className="border-t border-gray-200 pt-4 mt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Advanced Options</h4>

          <div className="space-y-4">
            <DateTimePicker
              label="Due Date"
              value={dueDate}
              onChange={setDueDate}
              minDate={getCurrentLocalTime()}
            />

            <DateTimePicker
              label="Reminder"
              value={reminderTime}
              onChange={setReminderTime}
              minDate={getCurrentLocalTime()}
            />

            <RecurrenceSelector value={recurrencePattern} onChange={setRecurrencePattern} />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4 border-t border-gray-200">
          <Button type="submit" variant="primary" isLoading={isLoading}>
            {isLoading
              ? mode === 'create'
                ? 'Creating...'
                : 'Saving...'
              : mode === 'create'
              ? 'Create Task'
              : 'Save Changes'}
          </Button>
          <Button type="button" variant="ghost" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        </div>
      </div>
    </form>
  );
}
