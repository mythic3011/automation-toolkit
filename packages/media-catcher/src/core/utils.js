/**
 * Utility functions
 */

/**
 * Get page title (sanitized for filename)
 */
export function getPageTitle() {
  let title = document.title || "media-capture";
  // Remove invalid filename characters
  title = title.replace(/[<>:"/\\|?*]/g, "-");
  // Trim and limit length
  title = title.trim().substring(0, 100);
  return title || "media-capture";
}

/**
 * Create ISO format filename
 */
export function createFilename(extension = "json") {
  const now = new Date();
  const isoString = now.toISOString().replace(/[:.]/g, "-").replace("Z", "");
  const title = getPageTitle();
  return `${title}_${isoString}.${extension}`;
}

/**
 * Format date/time for display
 */
export function formatDateTime(date) {
  return date.toLocaleString();
}

/**
 * Optimized hash generation using FNV-1a algorithm
 */
export function generateHash(data) {
  const str = JSON.stringify(data);
  let hash = 2166136261; // FNV offset basis

  for (let i = 0, len = str.length; i < len; i++) {
    hash ^= str.charCodeAt(i);
    hash +=
      (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }

  return (hash >>> 0).toString(36);
}

/**
 * Debounce utility for performance
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Detect if response is VTT format
 */
export function isVTTFormat(data) {
  if (typeof data !== "string") return false;
  return data.trim().startsWith("WEBVTT") || data.includes("-->");
}
