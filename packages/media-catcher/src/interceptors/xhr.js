/**
 * XMLHttpRequest interception
 */

import { CONFIG } from "../core/config.js";
import { isVTTFormat } from "../core/utils.js";
import { handleCapturedResponse } from "../handlers/response.js";

// Override XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
const originalSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function (method, url, ...rest) {
  this._method = method;
  // Normalise URL to string (XHR open() accepts URL objects in some browsers)
  this._url = url == null ? "" : String(url);

  // Log only relevant requests (avoid spamming console on every POST/GET)
  if (method === "POST" && this._url.includes(CONFIG.PANOPTO_URL_PATTERN)) {
    console.log("[Media Catcher] POST Panopto request detected:", this._url);
  }
  if (method === "GET" && this._url.includes(CONFIG.ZOOM_VTT_PATTERN)) {
    console.log("[Media Catcher] GET Zoom VTT request detected:", this._url);
  }

  return originalOpen.call(this, method, url, ...rest);
};

XMLHttpRequest.prototype.send = function (data) {
  const xhr = this;

  // Check if this is Panopto JSON request
  const isPanoptoRequest =
    xhr._method === "POST" &&
    xhr._url &&
    xhr._url.includes(CONFIG.PANOPTO_URL_PATTERN);

  // Check if this is Zoom VTT request
  const isZoomVTTRequest =
    xhr._method === "GET" &&
    xhr._url &&
    xhr._url.includes(CONFIG.ZOOM_VTT_PATTERN);

  if (isPanoptoRequest || isZoomVTTRequest) {
    const requestType = isPanoptoRequest ? "Panopto JSON" : "Zoom VTT";
    console.log(`[Media Catcher] 🎯 ${requestType} REQUEST INTERCEPTED!`);
    console.log("[Media Catcher] URL:", xhr._url);
    if (isPanoptoRequest) {
      console.log("[Media Catcher] Request data:", data);
    }

    // Store original onload handler
    const originalOnLoad = xhr.onload;
    const originalOnReadyStateChange = xhr.onreadystatechange;

    // Flag to prevent duplicate captures
    let captured = false;

    // Override onreadystatechange to catch response
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200 && !captured) {
        try {
          if (isPanoptoRequest) {
            const responseData = JSON.parse(xhr.responseText);
            captured = true;
            handleCapturedResponse(responseData, "json");
          } else if (isZoomVTTRequest) {
            const vttData = xhr.responseText;
            if (isVTTFormat(vttData)) {
              captured = true;
              handleCapturedResponse(vttData, "vtt");
            } else {
              console.warn(
                "[Media Catcher] Response doesn't look like VTT format"
              );
            }
          }
        } catch (e) {
          console.error("[Media Catcher] Error parsing response:", e);
        }
      }

      // Call original handler if exists
      if (originalOnReadyStateChange) {
        return originalOnReadyStateChange.apply(this, arguments);
      }
    };

    // Also override onload as backup
    xhr.onload = function () {
      if (xhr.status === 200 && !captured) {
        try {
          if (isPanoptoRequest) {
            const responseData = JSON.parse(xhr.responseText);
            captured = true;
            handleCapturedResponse(responseData, "json");
          } else if (isZoomVTTRequest) {
            const vttData = xhr.responseText;
            if (isVTTFormat(vttData)) {
              captured = true;
              handleCapturedResponse(vttData, "vtt");
            } else {
              console.warn(
                "[Media Catcher] Response doesn't look like VTT format"
              );
            }
          }
        } catch (e) {
          console.error("[Media Catcher] Error parsing response:", e);
        }
      }

      // Call original handler if exists
      if (originalOnLoad) {
        return originalOnLoad.apply(this, arguments);
      }
    };
  }

  return originalSend.call(this, data);
};

export function setupXHRInterceptor() {
  console.log("[Media Catcher] XHR interceptor installed");
}
