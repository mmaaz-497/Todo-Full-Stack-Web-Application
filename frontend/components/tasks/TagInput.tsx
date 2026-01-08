'use client';

import React, { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  userId: string;
  className?: string;
}

/**
 * TagInput Component
 *
 * Intermediate Feature: Tag input with autocomplete
 * - Add/remove tags as chips
 * - Autocomplete from user's existing tags
 * - Max 10 tags, each max 30 chars
 * - Alphanumeric + hyphen/underscore only
 */
export default function TagInput({ value, onChange, userId, className = '' }: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch user's existing tags for autocomplete
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const tags = await api.getUserTags(userId);
        setAllTags(tags);
      } catch (error) {
        console.error('Failed to fetch tags:', error);
      }
    };

    fetchTags();
  }, [userId]);

  // Filter suggestions based on input
  useEffect(() => {
    if (inputValue.trim()) {
      const filtered = allTags.filter(
        (tag) =>
          tag.toLowerCase().includes(inputValue.toLowerCase()) &&
          !value.includes(tag)
      );
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [inputValue, allTags, value]);

  const addTag = (tag: string) => {
    const normalized = tag.toLowerCase().trim();

    // Validation
    if (!normalized) return;

    if (value.length >= 10) {
      alert('Maximum 10 tags allowed');
      return;
    }

    if (normalized.length > 30) {
      alert('Tag cannot exceed 30 characters');
      return;
    }

    if (!/^[a-z0-9_-]+$/.test(normalized)) {
      alert('Tags can only contain letters, numbers, hyphens, and underscores');
      return;
    }

    if (value.includes(normalized)) {
      alert('Tag already added');
      return;
    }

    onChange([...value, normalized]);
    setInputValue('');
    setShowSuggestions(false);
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (inputValue.trim()) {
        addTag(inputValue);
      }
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <label className="text-sm font-medium text-gray-700">
        Tags <span className="text-gray-500">({value.length}/10)</span>
      </label>

      {/* Tag chips */}
      <div className="flex flex-wrap gap-2 mb-2">
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="hover:text-indigo-600 focus:outline-none"
              aria-label={`Remove tag ${tag}`}
            >
              ×
            </button>
          </span>
        ))}
      </div>

      {/* Input with autocomplete */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => inputValue && setShowSuggestions(suggestions.length > 0)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="Type to add tags..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          disabled={value.length >= 10}
        />

        {/* Autocomplete suggestions */}
        {showSuggestions && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-40 overflow-y-auto">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addTag(suggestion)}
                className="w-full text-left px-3 py-2 hover:bg-indigo-50 focus:bg-indigo-50 focus:outline-none"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>

      <p className="text-xs text-gray-500">
        Press Enter to add. Max 30 chars per tag. Letters, numbers, hyphens, underscores only.
      </p>
    </div>
  );
}
