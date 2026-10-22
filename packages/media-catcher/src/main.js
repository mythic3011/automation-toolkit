/**
 * Media Catcher - Main Entry Point
 * Version 2.4 - Modular Architecture
 */

// Import all modules
import { setupXHRInterceptor } from "./interceptors/xhr.js";
import { setupFetchInterceptor } from "./interceptors/fetch.js";
import { createGUI, setupPublicAPI } from "./ui/gui.js";

console.log("[Media Catcher] Script loaded - Version 2.4 (Panopto + Zoom)");
console.log("[Media Catcher] Current URL:", window.location.href);
console.log("[Media Catcher] Document ready state:", document.readyState);

// Install interceptors
setupXHRInterceptor();
setupFetchInterceptor();

// Mark interceptors as installed
window._mediaCatcherInstalled = true;

console.log(
  "[Media Catcher] XHR and Fetch interceptors installed for Panopto & Zoom"
);

// Setup public API
setupPublicAPI();

// Show welcome message
console.log("═══════════════════════════════════════");
console.log("🎯 Media Catcher Loaded! (Panopto + Zoom)");
console.log("═══════════════════════════════════════");
console.log("Supports:");
console.log("  📹 Panopto JSON (captions/delivery info)");
console.log("  📹 Zoom VTT (transcript subtitles)");
console.log("");
console.log("Type 'panoptoCatcher.help()' for commands");
console.log("Type 'panoptoCatcher.status()' to check status");
console.log("═══════════════════════════════════════");

// Initialize GUI when DOM is ready
function initializeGUI() {
  console.log("[Media Catcher] Initializing GUI...");
  console.log("[Media Catcher] Document ready state:", document.readyState);

  if (document.body) {
    createGUI();
  } else {
    console.log("[Media Catcher] Body not ready, waiting...");
    setTimeout(initializeGUI, 100);
  }
}

// Multiple initialization methods for reliability
if (document.readyState === "loading") {
  console.log(
    "[Media Catcher] Document still loading, adding DOMContentLoaded listener"
  );
  document.addEventListener("DOMContentLoaded", initializeGUI);
  // Backup timer
  setTimeout(initializeGUI, 2000);
} else {
  console.log(
    "[Media Catcher] Document already loaded, initializing immediately"
  );
  initializeGUI();
}

// Additional fallback for SPA navigation
if (window.location.href.includes("panopto.com")) {
  console.log("[Media Catcher] Panopto detected, setting up fallback timer");
  setTimeout(() => {
    if (!document.getElementById("panopto-catcher-toggle-btn")) {
      console.log("[Media Catcher] GUI not found, attempting to create...");
      initializeGUI();
    }
  }, 3000);
}

console.log("[Media Catcher] Initialization complete");
