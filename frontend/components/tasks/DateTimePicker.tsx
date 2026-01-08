'use client';

import React from 'react';

interface DateTimePickerProps {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  minDate?: string;
  className?: string;
  required?: boolean;
}

/**
 * DateTimePicker Component
 *
 * Advanced Feature: Date and time picker for due dates and reminders
 * - HTML5 datetime-local input
 * - Validation for min date
 * - Clear button for optional fields
 */
export default function DateTimePicker({
  label,
  value,
  onChange,
  minDate,
  className = '',
  required = false,
}: DateTimePickerProps) {
  // Convert ISO string to datetime-local format (YYYY-MM-DDTHH:mm)
  // Database stores Pakistan local time (no timezone), display as-is
  const formatDateTimeLocal = (isoString: string | null): string => {
    if (!isoString) return '';

    const trimmed = isoString.trim();
    const [datePart, timePart] = trimmed.split('T');
    if (!datePart || !timePart) return '';

    const [year, month, day] = datePart.split('-').map(Number);
    const [hours, minutes] = timePart.split(':').map(Number);

    // Create date object in local time - Pakistan time value stays as-is
    const date = new Date(year, month - 1, day, hours, minutes || 0);

    // Verify the date is valid
    if (isNaN(date.getTime())) return '';

    // Format for datetime-local input
    const yearStr = date.getFullYear();
    const monthStr = String(date.getMonth() + 1).padStart(2, '0');
    const dayStr = String(date.getDate()).padStart(2, '0');
    const hoursStr = String(date.getHours()).padStart(2, '0');
    const minutesStr = String(date.getMinutes()).padStart(2, '0');

    return `${yearStr}-${monthStr}-${dayStr}T${hoursStr}:${minutesStr}`;
  };

  // Convert datetime-local format to ISO string WITHOUT timezone
  // The local time picked is already Pakistan time, send as-is
  const parseToISO = (dateTimeLocal: string): string => {
    if (!dateTimeLocal) return '';

    const parts = dateTimeLocal.split('T');
    if (parts.length !== 2) return '';

    const [datePart, timePart] = parts;
    const timeParts = timePart.split(':');
    const hours = timeParts[0] || '00';
    const minutes = timeParts[1] || '00';
    const seconds = timeParts[2] || '00';

    // Parse as local datetime to validate
    const [year, month, day] = datePart.split('-').map(Number);
    const date = new Date(year, month - 1, day, parseInt(hours), parseInt(minutes), parseInt(seconds));

    // Verify the date is valid
    if (isNaN(date.getTime())) return '';

    // Return as simple ISO format without timezone (YYYY-MM-DDTHH:mm:ss)
    // Backend will store this as Pakistan local time
    return `${datePart}T${hours}:${minutes}:${seconds}`;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue ? parseToISO(newValue) : null);
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <label className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative flex items-center gap-2">
        <input
          type="datetime-local"
          value={formatDateTimeLocal(value)}
          onChange={handleChange}
          min={minDate ? formatDateTimeLocal(minDate) : undefined}
          required={required}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        {!required && value && (
          <button
            type="button"
            onClick={handleClear}
            className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 rounded-md"
            aria-label="Clear date"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
