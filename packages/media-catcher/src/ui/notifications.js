/**
 * Notification system
 */

import { CONFIG } from "../core/config.js";

/**
 * Show notification with requestAnimationFrame for smooth animation
 */
export function showNotification(message) {
  if (!document.body) return;

  const notification = document.createElement("div");
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    z-index: 9999999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    font-weight: 500;
    animation: slideDown 0.3s ease-out;
  `;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Use requestAnimationFrame for smoother animation
  requestAnimationFrame(() => {
    setTimeout(() => {
      requestAnimationFrame(() => {
        notification.style.transition = "opacity 0.3s";
        notification.style.opacity = "0";
        setTimeout(() => notification.remove(), 300);
      });
    }, CONFIG.NOTIFICATION_DURATION_MS);
  });
}
