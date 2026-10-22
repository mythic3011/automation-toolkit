/**
 * Response handling logic
 */

import { state } from "../core/state.js";
import { generateHash, createFilename } from "../core/utils.js";
import {
  isDuplicate,
  isTooSmall,
  enforceRequestLimit,
} from "../data/deduplication.js";
import { downloadJSON, downloadVTT } from "../data/downloader.js";
import { updateUI } from "../ui/gui.js";
import { showNotification } from "../ui/notifications.js";

/**
 * Handle captured response
 */
export function handleCapturedResponse(responseData, contentType = "json") {
  console.log("[Media Catcher] 📦 Response received, processing...");
  console.log("[Media Catcher] Content type:", contentType);

  // Calculate size based on content type
  const dataStr =
    typeof responseData === "string"
      ? responseData
      : JSON.stringify(responseData);
  const dataSize = dataStr.length;

  // Check if response is too small
  if (isTooSmall(dataSize)) {
    console.log(
      `[Media Catcher] ⚠️ Response too small (${dataSize} bytes < ${state.minSize} bytes), skipping`
    );
    showNotification(
      `⚠️ Skipped: Too small (${(dataSize / 1024).toFixed(2)} KB)`
    );
    return;
  }

  // Generate hash and check for duplicates
  const hash = generateHash(responseData);
  if (isDuplicate(hash)) {
    console.log("[Media Catcher] ⚠️ Duplicate response detected, skipping");
    showNotification("⚠️ Skipped: Duplicate packet");
    return;
  }

  const sizeKB = (dataSize / 1024).toFixed(2);
  console.log("[Media Catcher] ✅ Response is meaningful!");
  console.log("[Media Catcher] Size:", sizeKB, "KB");
  console.log("[Media Catcher] Response data:", responseData);

  // Add to captured requests
  const request = {
    timestamp: new Date(),
    data: responseData,
    hash: hash,
    size: dataSize,
    contentType: contentType,
    downloaded: false,
  };

  state.capturedRequests.push(request);
  state.requestHashes.add(hash);

  // Enforce request limit
  enforceRequestLimit();

  console.log(
    "[Media Catcher] Total captured requests:",
    state.capturedRequests.length
  );

  // Auto download if enabled
  if (state.autoDownload) {
    console.log("[Media Catcher] Auto-download is enabled, downloading...");

    if (contentType === "vtt") {
      const filename = createFilename("vtt");
      downloadVTT(responseData, filename);
    } else {
      const filename = createFilename("json");
      downloadJSON(responseData, filename);
    }

    request.downloaded = true;
  } else {
    console.log(
      "[Media Catcher] Auto-download is disabled, storing for manual download"
    );
  }

  updateUI();

  // Show notification
  const typeLabel = contentType === "vtt" ? "VTT" : "JSON";
  showNotification(
    `✅ Captured ${typeLabel}! ${sizeKB} KB (Total: ${state.capturedRequests.length})`
  );
}
