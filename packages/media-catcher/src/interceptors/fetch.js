/**
 * Fetch API interception
 */

import { CONFIG } from "../core/config.js";
import { isVTTFormat } from "../core/utils.js";
import { handleCapturedResponse } from "../handlers/response.js";

// Intercept fetch API as backup
const originalFetch = window.fetch;

window.fetch = function (...args) {
  const [urlOrRequest, options] = args;

  // fetch() accepts a string, URL, or Request object — normalise to a string
  const url =
    typeof urlOrRequest === "string"
      ? urlOrRequest
      : urlOrRequest && typeof urlOrRequest.url === "string"
        ? urlOrRequest.url
        : String(urlOrRequest || "");

  const method = (
    (options && options.method) ||
    (urlOrRequest && typeof urlOrRequest === "object" && urlOrRequest.method) ||
    "GET"
  ).toUpperCase();

  const isPanoptoRequest =
    method === "POST" && url.includes(CONFIG.PANOPTO_URL_PATTERN);

  const isZoomVTTRequest = url.includes(CONFIG.ZOOM_VTT_PATTERN);

  if (isPanoptoRequest || isZoomVTTRequest) {
    const requestType = isPanoptoRequest ? "Panopto JSON" : "Zoom VTT";
    console.log(`[Media Catcher] Intercepted fetch ${requestType} request`);

    return originalFetch.apply(this, args).then((response) => {
      // Clone the response so we can read it
      const clonedResponse = response.clone();

      if (isPanoptoRequest) {
        clonedResponse
          .json()
          .then((data) => {
            handleCapturedResponse(data, "json");
          })
          .catch((e) => {
            console.error("[Media Catcher] Error parsing fetch response:", e);
          });
      } else if (isZoomVTTRequest) {
        clonedResponse
          .text()
          .then((vttData) => {
            if (isVTTFormat(vttData)) {
              handleCapturedResponse(vttData, "vtt");
            } else {
              console.warn(
                "[Media Catcher] Response doesn't look like VTT format"
              );
            }
          })
          .catch((e) => {
            console.error("[Media Catcher] Error reading VTT response:", e);
          });
      }

      return response;
    });
  }

  return originalFetch.apply(this, args);
};

export function setupFetchInterceptor() {
  console.log("[Media Catcher] Fetch interceptor installed");
}
