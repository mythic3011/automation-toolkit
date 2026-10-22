/**
 * GUI creation and management
 */

import { state, DOM, cacheDOMElements } from "../core/state.js";
import { CONFIG } from "../core/config.js";
import { formatDateTime, debounce, getPageTitle } from "../core/utils.js";
import { downloadJSON, downloadVTT } from "../data/downloader.js";
import { injectStyles } from "./styles.js";
import { showNotification } from "./notifications.js";
import { showConfirmDialog } from "./dialogs.js";

/**
 * Toggle panel visibility
 */
export function togglePanel() {
  state.isPanelVisible = !state.isPanelVisible;
  const panel = document.getElementById("panopto-catcher-panel");
  if (state.isPanelVisible) {
    panel.classList.add("visible");
  } else {
    panel.classList.remove("visible");
  }
}

/**
 * Toggle auto download
 */
export function toggleAutoDownload() {
  state.autoDownload = !state.autoDownload;
  updateUI();
  console.log("[Media Catcher] Auto download:", state.autoDownload);
}

/**
 * Toggle clean data
 */
export function toggleCleanData() {
  state.cleanData = !state.cleanData;
  updateUI();
  console.log("[Media Catcher] Clean data:", state.cleanData);
}

/**
 * Toggle deduplication
 */
export function toggleDeduplication() {
  state.deduplication = !state.deduplication;
  updateUI();
  console.log("[Media Catcher] Deduplication:", state.deduplication);
}

/**
 * Clear all requests
 */
export function clearAllRequests() {
  showConfirmDialog(
    "Are you sure you want to clear all captured requests? This cannot be undone.",
    () => {
      state.capturedRequests = [];
      state.requestHashes.clear();
      updateUI();
      showNotification("🗑️ All requests cleared!");
    }
  );
}

/**
 * Update UI using cached DOM elements
 */
function updateUIInternal() {
  // Use cached DOM elements
  if (!DOM.statCaptured) return; // GUI not ready yet

  const requestCount = state.capturedRequests.length;
  const downloadedCount = state.capturedRequests.filter(
    (r) => r.downloaded
  ).length;

  // Update stats
  DOM.statCaptured.textContent = requestCount;
  DOM.statDownloaded.textContent = downloadedCount;

  // Update toggles using classList.toggle for better performance
  DOM.autoDownloadToggle.classList.toggle("active", state.autoDownload);
  DOM.cleanDataToggle.classList.toggle("active", state.cleanData);
  DOM.deduplicationToggle.classList.toggle("active", state.deduplication);

  // Update badge
  const existingBadge = DOM.toggleBtn.querySelector(".badge");
  if (requestCount > 0) {
    if (!existingBadge) {
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = requestCount;
      DOM.toggleBtn.appendChild(badge);
    } else {
      existingBadge.textContent = requestCount;
    }
  } else if (existingBadge) {
    existingBadge.remove();
  }

  // Update requests list
  if (requestCount === 0) {
    DOM.requestsList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <div>No requests captured yet</div>
      </div>
    `;
  } else {
    const reversedRequests = [...state.capturedRequests].reverse();

    DOM.requestsList.innerHTML = reversedRequests
      .map((req, index) => {
        const originalIndex = requestCount - 1 - index;
        const sizeKB = (req.size / 1024).toFixed(2);
        const typeLabel = req.contentType === "vtt" ? "VTT" : "JSON";
        const typeIcon = req.contentType === "vtt" ? "📝" : "📋";
        return `
          <div class="request-item">
            <div class="request-time">⏰ ${formatDateTime(req.timestamp)}</div>
            <div style="color: #333; font-weight: 500; margin-bottom: 4px;">
              ${req.downloaded ? "✅" : "⏳"} ${typeIcon} ${typeLabel} #${originalIndex + 1}
            </div>
            <div style="font-size: 11px; color: #999;">
              Size: ${sizeKB} KB
            </div>
            <div class="request-actions">
              <button class="btn btn-primary" onclick="window.panoptoCatcher.download(${originalIndex})">
                💾 Download
              </button>
              <button class="btn btn-secondary" onclick="window.panoptoCatcher.view(${originalIndex})">
                👁️ View
              </button>
            </div>
          </div>
    `;
      })
      .join("");
  }
}

// Debounced updateUI for performance
export const updateUI = debounce(updateUIInternal, CONFIG.UPDATE_DEBOUNCE_MS);

/**
 * Make element draggable
 */
function makeDraggable(element, handle) {
  let pos1 = 0,
    pos2 = 0,
    pos3 = 0,
    pos4 = 0;

  handle.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = element.offsetTop - pos2 + "px";
    element.style.left = element.offsetLeft - pos1 + "px";
    element.style.right = "auto";
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

/**
 * Create GUI
 */
export function createGUI() {
  try {
    console.log("[Media Catcher] Creating GUI...");

    // Check if document.body exists
    if (!document.body) {
      console.error(
        "[Media Catcher] document.body not available yet, retrying..."
      );
      setTimeout(createGUI, 100);
      return;
    }

    // Check if GUI already exists
    if (document.getElementById("panopto-catcher-toggle-btn")) {
      console.log("[Media Catcher] GUI already exists, skipping creation");
      cacheDOMElements();
      return;
    }

    // Inject styles first
    injectStyles();

    // Create floating button
    const toggleBtn = document.createElement("button");
    toggleBtn.id = "panopto-catcher-toggle-btn";
    toggleBtn.innerHTML = "📥";
    toggleBtn.title = "Toggle XHR Catcher Panel";

    // Create panel
    const panel = document.createElement("div");
    panel.id = "panopto-catcher-panel";
    panel.innerHTML = `
      <div id="panopto-catcher-header">
        <h3>🎯 Media Catcher (Panopto + Zoom)</h3>
        <button id="panopto-catcher-close">×</button>
      </div>
      <div id="panopto-catcher-body">
        <div class="catcher-control">
          <div class="catcher-toggle">
            <label>Auto Download</label>
            <div class="toggle-switch" id="auto-download-toggle"></div>
          </div>
          <div class="catcher-toggle">
            <label>Clean Useless Fields</label>
            <div class="toggle-switch active" id="clean-data-toggle"></div>
          </div>
          <div class="catcher-toggle">
            <label>Filter Duplicates</label>
            <div class="toggle-switch active" id="deduplication-toggle"></div>
          </div>
        </div>
        
        <div class="catcher-stats">
          <div class="stat-box">
            <span class="stat-value" id="stat-captured">0</span>
            <span class="stat-label">Captured</span>
          </div>
          <div class="stat-box">
            <span class="stat-value" id="stat-downloaded">0</span>
            <span class="stat-label">Downloaded</span>
          </div>
        </div>
        
        <h4 style="margin: 0 0 10px 0; color: #333; font-size: 14px;">📋 Captured Requests</h4>
        <div class="requests-list" id="requests-list">
          <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div>No requests captured yet</div>
          </div>
        </div>
        
        <button class="btn btn-clear" id="clear-all-btn">🗑️ Clear All</button>
      </div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(panel);
    console.log("[Media Catcher] GUI elements appended to body");

    // Event listeners
    toggleBtn.addEventListener("click", togglePanel);
    panel
      .querySelector("#panopto-catcher-close")
      .addEventListener("click", togglePanel);
    panel
      .querySelector("#auto-download-toggle")
      .addEventListener("click", toggleAutoDownload);
    panel
      .querySelector("#clean-data-toggle")
      .addEventListener("click", toggleCleanData);
    panel
      .querySelector("#deduplication-toggle")
      .addEventListener("click", toggleDeduplication);
    panel
      .querySelector("#clear-all-btn")
      .addEventListener("click", clearAllRequests);

    console.log("[Media Catcher] Event listeners attached");

    // Make panel draggable
    makeDraggable(panel, panel.querySelector("#panopto-catcher-header"));

    // Cache DOM elements for performance
    cacheDOMElements();

    updateUI();
    console.log("[Media Catcher] GUI created successfully!");
  } catch (error) {
    console.error("[Media Catcher] Error creating GUI:", error);
  }
}

/**
 * Public API for button callbacks and debugging
 */
export function setupPublicAPI() {
  window.panoptoCatcher = {
    download: function (index) {
      const req = state.capturedRequests[index];
      if (req) {
        const extension = req.contentType === "vtt" ? "vtt" : "json";
        const filename = `${getPageTitle()}_${formatDateTime(
          req.timestamp
        ).replace(/[/,:]/g, "-")}.${extension}`;

        if (req.contentType === "vtt") {
          downloadVTT(req.data, filename);
        } else {
          downloadJSON(req.data, filename);
        }

        req.downloaded = true;
        updateUI();
      }
    },
    view: function (index) {
      const req = state.capturedRequests[index];
      if (req) {
        const typeLabel = req.contentType === "vtt" ? "VTT" : "JSON";
        console.log(
          `[Media Catcher] ${typeLabel} Request #${index + 1} Data:`,
          req.data
        );
        console.log(`[Media Catcher] Size: ${(req.size / 1024).toFixed(2)} KB`);
        console.log(
          `[Media Catcher] Captured at: ${formatDateTime(req.timestamp)}`
        );
        showNotification("👁️ Data logged to console! Check DevTools (F12)");
      }
    },
    status: function () {
      console.log("═══════════════════════════════════════");
      console.log("📊 Media Catcher Status");
      console.log("═══════════════════════════════════════");
      console.log("✅ Script loaded:", true);
      console.log(
        "✅ Interceptors installed:",
        typeof window._mediaCatcherInstalled !== "undefined"
      );
      console.log(
        "📦 GUI button exists:",
        !!document.getElementById("panopto-catcher-toggle-btn")
      );
      console.log(
        "📦 GUI panel exists:",
        !!document.getElementById("panopto-catcher-panel")
      );
      console.log("🔄 Auto-download enabled:", state.autoDownload);
      console.log("🧹 Clean data enabled:", state.cleanData);
      console.log("🔁 Deduplication enabled:", state.deduplication);
      console.log("📏 Minimum size:", state.minSize, "bytes");
      console.log("📥 Requests captured:", state.capturedRequests.length);
      console.log(
        "💾 Requests downloaded:",
        state.capturedRequests.filter((r) => r.downloaded).length
      );
      console.log("🌐 Current URL:", window.location.href);
      console.log("═══════════════════════════════════════");
      return {
        loaded: true,
        interceptorsInstalled:
          typeof window._mediaCatcherInstalled !== "undefined",
        guiExists: !!document.getElementById("panopto-catcher-toggle-btn"),
        autoDownload: state.autoDownload,
        cleanData: state.cleanData,
        deduplication: state.deduplication,
        minSize: state.minSize,
        capturedCount: state.capturedRequests.length,
        downloadedCount: state.capturedRequests.filter((r) => r.downloaded)
          .length,
      };
    },
    showPanel: function () {
      state.isPanelVisible = true;
      const panel = document.getElementById("panopto-catcher-panel");
      if (panel) {
        panel.classList.add("visible");
        console.log("[Media Catcher] Panel shown");
      } else {
        console.error("[Media Catcher] Panel not found!");
      }
    },
    help: function () {
      console.log("═══════════════════════════════════════");
      console.log("🎯 Media Catcher - Help (Panopto + Zoom)");
      console.log("═══════════════════════════════════════");
      console.log("Available commands:");
      console.log("  panoptoCatcher.status()    - Show current status");
      console.log("  panoptoCatcher.showPanel() - Show the GUI panel");
      console.log("  panoptoCatcher.help()      - Show this help");
      console.log("");
      console.log("Supported Platforms:");
      console.log("  📹 Panopto - JSON delivery info (captions, streams)");
      console.log("  📹 Zoom - VTT transcript files (subtitles)");
      console.log("");
      console.log("Features:");
      console.log("  ✅ Auto Download - Automatically save captured requests");
      console.log(
        "  🧹 Clean Data - Remove null/empty/useless fields from JSON"
      );
      console.log("  🔁 Deduplication - Skip duplicate/same responses");
      console.log("  📏 Size Filter - Skip small packets (<100 bytes)");
      console.log("  💾 Manual Download - Download any captured request later");
      console.log("  👁️  View Data - Inspect request data in console");
      console.log("═══════════════════════════════════════");
    },
  };
}
