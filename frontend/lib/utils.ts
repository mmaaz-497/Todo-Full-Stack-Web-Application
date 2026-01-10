/**
 * Safe Browser API Utilities
 *
 * Utility functions to safely access browser-specific APIs like localStorage and window
 * during both client-side runtime and server-side rendering/build.
 */

/**
 * Checks if the code is running in a browser environment
 */
export const isBrowser = (): boolean => {
  return typeof window !== 'undefined';
};

/**
 * Safely gets an item from localStorage
 */
export const safeLocalStorageGetItem = (key: string): string | null => {
  if (!isBrowser()) {
    return null;
  }
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
};

/**
 * Safely sets an item in localStorage
 */
export const safeLocalStorageSetItem = (key: string, value: string): void => {
  if (!isBrowser()) {
    return;
  }
  try {
    localStorage.setItem(key, value);
  } catch {
    // Silently fail if localStorage is not available
  }
};

/**
 * Safely removes an item from localStorage
 */
export const safeLocalStorageRemoveItem = (key: string): void => {
  if (!isBrowser()) {
    return;
  }
  try {
    localStorage.removeItem(key);
  } catch {
    // Silently fail if localStorage is not available
  }
};

/**
 * Safely accesses the window.location object
 */
export const safeWindowLocation = (): Pick<Location, 'href' | 'pathname'> | null => {
  if (!isBrowser()) {
    return null;
  }
  try {
    return {
      href: window.location.href,
      pathname: window.location.pathname,
    };
  } catch {
    return null;
  }
};

/**
 * Safely redirects using window.location
 */
export const safeRedirect = (url: string): void => {
  if (!isBrowser()) {
    return;
  }
  try {
    window.location.href = url;
  } catch {
    // Silently fail if window.location is not accessible
  }
};