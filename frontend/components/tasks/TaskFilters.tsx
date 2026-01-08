'use client';

import React, { useState, useEffect } from 'react';
import { TaskFilters as Filters, TaskPriority } from '@/lib/api';
import { api } from '@/lib/api';

interface TaskFiltersProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  userId: string;
  onSearch: (query: string) => void;
  className?: string;
}

/**
 * TaskFilters Component
 *
 * Intermediate Features: Search, filter, and sort controls
 * - Search by keyword
 * - Filter by priority (HIGH/MEDIUM/LOW/all)
 * - Filter by status (all/pending/completed)
 * - Filter by tags (multi-select)
 * - Sort by (created_date/due_date/priority/title)
 */
export default function TaskFilters({ filters, onChange, userId, onSearch, className = '' }: TaskFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [allTags, setAllTags] = useState<string[]>([]);

  // Fetch user's tags for filter options
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

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
    }
  };

  const handlePriorityChange = (priority: string) => {
    onChange({
      ...filters,
      priority: priority as TaskPriority | 'all',
    });
  };

  const handleStatusChange = (status: string) => {
    onChange({
      ...filters,
      status: status as 'all' | 'pending' | 'completed',
    });
  };

  const handleSortChange = (sort: string) => {
    onChange({
      ...filters,
      sort: sort as 'created_date' | 'due_date' | 'priority' | 'title',
    });
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag];

    onChange({
      ...filters,
      tags: newTags,
    });
  };

  const clearAllFilters = () => {
    onChange({
      priority: 'all',
      status: 'all',
      tags: [],
      sort: 'created_date',
    });
    setSearchQuery('');
  };

  const hasActiveFilters =
    filters.priority !== 'all' ||
    filters.status !== 'all' ||
    (filters.tags && filters.tags.length > 0) ||
    filters.sort !== 'created_date';

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}>
      <div className="space-y-4">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks by title or description..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            Search
          </button>
        </form>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Priority Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filters.priority || 'all'}
              onChange={(e) => handlePriorityChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="all">All Priorities</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status || 'all'}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="all">All Tasks</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          {/* Sort */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={filters.sort || 'created_date'}
              onChange={(e) => handleSortChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            >
              <option value="created_date">Created Date (Newest)</option>
              <option value="due_date">Due Date (Nearest)</option>
              <option value="priority">Priority (High to Low)</option>
              <option value="title">Title (A-Z)</option>
            </select>
          </div>

          {/* Clear Filters Button */}
          <div className="flex items-end">
            <button
              type="button"
              onClick={clearAllFilters}
              disabled={!hasActiveFilters}
              className={`w-full px-4 py-2 rounded-md font-medium ${
                hasActiveFilters
                  ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Tag Filter */}
        {allTags.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Tags</label>
            <div className="flex flex-wrap gap-2">
              {allTags.map((tag) => {
                const isSelected = filters.tags?.includes(tag);
                return (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => handleTagToggle(tag)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      isSelected
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {tag}
                    {isSelected && ' ✓'}
                  </button>
                );
              })}
            </div>
            {filters.tags && filters.tags.length > 0 && (
              <p className="text-xs text-gray-500 mt-2">
                Showing tasks with ALL selected tags ({filters.tags.length})
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
