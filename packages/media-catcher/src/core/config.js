/**
 * Configuration constants for Media Catcher
 */

export const CONFIG = {
  MIN_SIZE_BYTES: 100, // Lower for VTT files
  MAX_REQUESTS_STORED: 50,
  UPDATE_DEBOUNCE_MS: 100,
  NOTIFICATION_DURATION_MS: 2000,
  PANOPTO_URL_PATTERN: "/Panopto/Pages/Viewer/DeliveryInfo.aspx",
  ZOOM_VTT_PATTERN: "/rec/play/vtt",
};

export const USELESS_VALUES = new Set([
  null,
  false,
  0,
  "",
  "00000000-0000-0000-0000-000000000000",
  "/Date(-11644473600000)/",
]);

export const USERSCRIPT_METADATA = {
  name: "Media Catcher (Panopto & Zoom)",
  namespace: "http://tampermonkey.net/",
  version: "2.4",
  description: "Catch and save Panopto JSON & Zoom VTT transcripts with GUI",
  author: "Automation Toolkit contributors",
  matches: [
    "https://polyu.ap.panopto.com/*",
    "https://*.panopto.com/*",
    "http://polyu.ap.panopto.com/*",
    "http://*.panopto.com/*",
    "https://polyu.zoom.us/*",
    "https://*.zoom.us/*",
  ],
  grant: "none",
  runAt: "document-end",
};
