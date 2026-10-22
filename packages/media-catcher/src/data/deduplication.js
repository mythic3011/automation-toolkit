/**
 * Duplicate detection and request management
 */

import { CONFIG } from "../core/config.js";
import { state } from "../core/state.js";

/**
 * Check if response is a duplicate using hash
 */
export function isDuplicate(hash) {
  if (!state.deduplication) return false;
  return state.requestHashes.has(hash);
}

/**
 * Check if response is too small (accepts pre-calculated size)
 */
export function isTooSmall(size) {
  return size < state.minSize;
}

/**
 * Limit stored requests to prevent memory issues
 */
export function enforceRequestLimit() {
  if (state.capturedRequests.length > CONFIG.MAX_REQUESTS_STORED) {
    const removed = state.capturedRequests.shift();
    state.requestHashes.delete(removed.hash);
    console.log("[Media Catcher] Removed oldest request (limit reached)");
  }
}
