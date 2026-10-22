/**
 * Global state management
 */

import { CONFIG } from "./config.js";

export const state = {
  autoDownload: false,
  cleanData: true,
  deduplication: true,
  minSize: CONFIG.MIN_SIZE_BYTES,
  capturedRequests: [],
  isPanelVisible: false,
  requestHashes: new Set(), // Fast lookup for duplicates
};

// DOM cache for performance
export const DOM = {
  panel: null,
  toggleBtn: null,
  statCaptured: null,
  statDownloaded: null,
  requestsList: null,
  autoDownloadToggle: null,
  cleanDataToggle: null,
  deduplicationToggle: null,
};

/**
 * Cache DOM elements after creation
 */
export function cacheDOMElements() {
  DOM.panel = document.getElementById("panopto-catcher-panel");
  DOM.toggleBtn = document.getElementById("panopto-catcher-toggle-btn");
  DOM.statCaptured = document.getElementById("stat-captured");
  DOM.statDownloaded = document.getElementById("stat-downloaded");
  DOM.requestsList = document.getElementById("requests-list");
  DOM.autoDownloadToggle = document.getElementById("auto-download-toggle");
  DOM.cleanDataToggle = document.getElementById("clean-data-toggle");
  DOM.deduplicationToggle = document.getElementById("deduplication-toggle");
}
