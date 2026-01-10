'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/auth';
import { api, Task, TaskCreate, TaskUpdate, TaskFilters as Filters } from '@/lib/api';
import Button from '@/components/ui/Button';

// Helper to convert Task (with null fields) to TaskUpdate format (with undefined fields)
const taskToFormData = (task: Task | null): Partial<TaskUpdate> | undefined => {
  if (!task) return undefined;
  return {
    title: task.title,
    description: task.description ?? undefined,
    priority: task.priority,
    tags: task.tags,
    due_date: task.due_date ?? undefined,
    reminder_time: task.reminder_time ?? undefined,
    recurrence_pattern: task.recurrence_pattern,
  };
};
import TaskForm from '@/components/tasks/TaskForm';
import TaskCard from '@/components/tasks/TaskCard';
import TaskFilters from '@/components/tasks/TaskFilters';

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [searchResults, setSearchResults] = useState<Task[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [user, setUser] = useState<any>(null);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [formLoading, setFormLoading] = useState(false);

  // Filter state
  const [filters, setFilters] = useState<Filters>({
    priority: 'all',
    status: 'all',
    tags: [],
    sort: 'created_date',
  });

  // Delete animation state
  const [removingId, setRemovingId] = useState<number | null>(null);

  useEffect(() => {
    // Check authentication
    const currentUser = auth.getCurrentUser();
    if (!currentUser) {
      router.push('/signin');
      return;
    }

    setUser(currentUser);
    loadTasks(currentUser.id);
  }, [router]);

  // Reload tasks when filters change
  useEffect(() => {
    if (user) {
      loadTasks(user.id);
      setSearchResults(null); // Clear search when filters change
    }
  }, [filters, user]);

  const loadTasks = async (userId: string) => {
    try {
      setLoading(true);
      const data = await api.getTasks(userId, filters);
      setTasks(data);
      setError('');
    } catch (err: any) {
      console.error('Load tasks error:', err);

      // Handle timeout or network errors
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Request timed out. Please check your connection and try again.');
      }
      // Handle authentication errors
      else if (err.response?.status === 401) {
        setError('Session expired. Please sign in again.');
        // Clear invalid session
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
        setTimeout(() => router.push('/signin'), 2000);
      }
      // Handle other errors
      else {
        setError(err.response?.data?.detail || 'Failed to load tasks. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignout = async () => {
    await auth.signout();
    router.push('/');
  };

  const handleSearch = async (query: string) => {
    if (!user) return;

    try {
      const results = await api.searchTasks(user.id, query);
      setSearchResults(results);
    } catch (err: any) {
      alert('Search failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    if (!user) return;

    setFormLoading(true);
    try {
      const task = await api.createTask(user.id, data);
      setTasks([task, ...tasks]);
      setShowForm(false);
      setFormMode('create');
    } catch (err: any) {
      alert('Failed to create task: ' + (err.response?.data?.detail || err.message));
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateTask = async (data: TaskUpdate) => {
    if (!user || !editingTask) return;

    setFormLoading(true);
    try {
      const updatedTask = await api.updateTask(user.id, editingTask.id, data);
      setTasks(tasks.map((t) => (t.id === editingTask.id ? updatedTask : t)));
      setShowForm(false);
      setFormMode('create');
      setEditingTask(null);
    } catch (err: any) {
      alert('Failed to update task: ' + (err.response?.data?.detail || err.message));
    } finally {
      setFormLoading(false);
    }
  };

  // Unified form submit handler that routes to create or update based on mode
  const handleFormSubmit = async (data: TaskCreate | TaskUpdate) => {
    if (formMode === 'create') {
      await handleCreateTask(data as TaskCreate);
    } else {
      await handleUpdateTask(data as TaskUpdate);
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    if (!user) return;

    try {
      const response = await api.toggleComplete(user.id, taskId);

      // Update the completed task
      setTasks(tasks.map((t) => (t.id === taskId ? response.task : t)));

      // If a new recurring instance was created, add it to the list
      if (response.next_occurrence) {
        setTasks([response.next_occurrence, ...tasks.map((t) => (t.id === taskId ? response.task : t))]);

        // Show notification
        alert(`Task completed! A new ${response.next_occurrence.recurrence_pattern} instance has been created.`);
      }
    } catch (err: any) {
      alert('Failed to update task');
    }
  };

  const handleStartEdit = (task: Task) => {
    setEditingTask(task);
    setFormMode('edit');
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setFormMode('create');
    setEditingTask(null);
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user) return;
    if (!confirm('Are you sure you want to delete this task?')) return;

    setRemovingId(taskId);

    // Wait for animation to complete
    setTimeout(async () => {
      try {
        await api.deleteTask(user.id, taskId);
        setTasks(tasks.filter((t) => t.id !== taskId));
        setRemovingId(null);
      } catch (err: any) {
        alert('Failed to delete task');
        setRemovingId(null);
      }
    }, 300);
  };

  const displayTasks = searchResults !== null ? searchResults : tasks;
  const completedCount = displayTasks.filter((t) => t.completed).length;
  const totalCount = displayTasks.length;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-center animate-fadeIn">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-neutral-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-50 animate-fadeIn min-h-screen">
      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Page Title */}
        <div className="mb-8 animate-slideDown">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 text-white text-2xl rounded-xl flex items-center justify-center shadow-lg">
                📝
              </div>
              <div>
                <h1 className="text-3xl font-bold text-neutral-900">My Tasks</h1>
                <p className="text-sm text-neutral-600 mt-1">
                  Manage and organize your tasks with priorities, tags, and reminders
                </p>
              </div>
            </div>

            <Button variant="ghost" onClick={handleSignout}>
              Sign Out
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-error-50 border-l-4 border-error-500 text-error-700 px-4 py-3 rounded animate-slideDown">
            {error}
          </div>
        )}

        {/* Filters */}
        {user && (
          <TaskFilters
            filters={filters}
            onChange={setFilters}
            userId={user.id}
            onSearch={handleSearch}
            className="mb-6"
          />
        )}

        {/* Search Results Indicator */}
        {searchResults !== null && (
          <div className="mb-4 bg-indigo-50 border-l-4 border-indigo-500 px-4 py-3 rounded flex items-center justify-between">
            <p className="text-indigo-700">
              Found {searchResults.length} search result{searchResults.length !== 1 ? 's' : ''}
            </p>
            <button
              onClick={() => setSearchResults(null)}
              className="text-indigo-700 hover:text-indigo-900 font-medium"
            >
              Clear Search
            </button>
          </div>
        )}

        {/* Progress Indicator */}
        {totalCount > 0 && (
          <div className="mb-6 bg-white rounded-xl p-6 shadow-sm border border-neutral-200 animate-slideDown">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700">Progress</span>
              <span className="text-sm font-semibold text-primary-600">{progress}%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-neutral-500">
              {completedCount} of {totalCount} tasks completed
            </p>
          </div>
        )}

        {/* Add Task Button */}
        {!showForm && (
          <div className="mb-6 sticky top-20 z-40 animate-slideDown">
            <button
              onClick={() => {
                setFormMode('create');
                setEditingTask(null);
                setShowForm(true);
              }}
              className="w-full bg-white rounded-xl shadow-lg border-2 border-primary-300 p-4 flex items-center justify-center gap-2 text-primary-600 hover:bg-primary-50 hover:border-primary-400 transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="font-semibold">Add New Task</span>
            </button>
          </div>
        )}

        {/* Task Form */}
        {showForm && user && (
          <div className="mb-6 animate-slideDown">
            <TaskForm
              mode={formMode}
              userId={user.id}
              initialData={taskToFormData(editingTask)}
              onSubmit={handleFormSubmit}
              onCancel={handleCancelForm}
              isLoading={formLoading}
            />
          </div>
        )}

        {/* Tasks List */}
        {displayTasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fadeIn">
            <div className="w-24 h-24 bg-neutral-100 rounded-full flex items-center justify-center mb-6">
              <svg className="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>

            <h3 className="text-2xl font-semibold text-neutral-900">
              {searchResults !== null ? 'No results found' : 'All caught up!'}
            </h3>

            <p className="mt-2 text-neutral-600 max-w-sm">
              {searchResults !== null
                ? 'Try adjusting your search query or filters'
                : 'No tasks found. Click the button above to add your first task.'}
            </p>

            {searchResults === null && (
              <Button
                variant="primary"
                size="lg"
                onClick={() => setShowForm(true)}
                className="mt-6"
              >
                Add Your First Task
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {displayTasks.map((task, index) => (
              <TaskCard
                key={task.id}
                task={task}
                isRemoving={removingId === task.id}
                animationDelay={index * 50}
                onToggleComplete={handleToggleComplete}
                onEdit={handleStartEdit}
                onDelete={handleDeleteTask}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
