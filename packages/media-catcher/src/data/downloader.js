/**
 * File download functionality
 */

import { cleanJSON } from "./cleaner.js";
import { state } from "../core/state.js";

/**
 * Download JSON as file
 */
export function downloadJSON(data, filename) {
  // Clean the data if enabled
  const cleanedData = cleanJSON(data);

  // Show comparison in console
  if (state.cleanData) {
    const originalSize = JSON.stringify(data).length;
    const cleanedSize = JSON.stringify(cleanedData).length;
    const savedBytes = originalSize - cleanedSize;
    const savedPercent = ((savedBytes / originalSize) * 100).toFixed(1);
    console.log(
      `[Media Catcher] Data cleaned: ${originalSize} → ${cleanedSize} bytes (saved ${savedPercent}%)`
    );
  }

  const blob = new Blob([JSON.stringify(cleanedData, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  console.log("[Media Catcher] Downloaded:", filename);
}

/**
 * Download VTT (text) file
 */
export function downloadVTT(data, filename) {
  const blob = new Blob([data], {
    type: "text/vtt",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  console.log("[Media Catcher] Downloaded VTT:", filename);
}
