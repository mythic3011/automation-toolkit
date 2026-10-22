/**
 * Modern confirmation dialogs
 */

/**
 * Show modern confirmation dialog
 */
export function showConfirmDialog(message, onConfirm) {
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99999999;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.2s ease-out;
  `;

  const dialog = document.createElement("div");
  dialog.style.cssText = `
    background: white;
    border-radius: 12px;
    padding: 24px;
    max-width: 400px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out;
  `;

  dialog.innerHTML = `
    <div style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #333;">
      ⚠️ Confirm Action
    </div>
    <div style="font-size: 14px; color: #666; margin-bottom: 20px; line-height: 1.5;">
      ${message}
    </div>
    <div style="display: flex; gap: 10px; justify-content: flex-end;">
      <button id="confirm-cancel" style="
        padding: 8px 16px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: #666;
        transition: all 0.2s;
      ">Cancel</button>
      <button id="confirm-ok" style="
        padding: 8px 16px;
        border: none;
        background: #e53e3e;
        color: white;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
      ">Confirm</button>
    </div>
  `;

  // Add hover effects
  const cancelBtn = dialog.querySelector("#confirm-cancel");
  const okBtn = dialog.querySelector("#confirm-ok");

  cancelBtn.onmouseenter = () => (cancelBtn.style.background = "#f7f7f7");
  cancelBtn.onmouseleave = () => (cancelBtn.style.background = "white");

  okBtn.onmouseenter = () => (okBtn.style.background = "#c53030");
  okBtn.onmouseleave = () => (okBtn.style.background = "#e53e3e");

  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  // ESC key to close (registered before cleanup so cleanup can detach it)
  const handleEsc = (e) => {
    if (e.key === "Escape") {
      cleanup();
    }
  };
  document.addEventListener("keydown", handleEsc);

  const cleanup = () => {
    document.removeEventListener("keydown", handleEsc);
    overlay.style.opacity = "0";
    setTimeout(() => overlay.remove(), 200);
  };

  cancelBtn.onclick = cleanup;
  okBtn.onclick = () => {
    cleanup();
    onConfirm();
  };
  overlay.onclick = (e) => {
    if (e.target === overlay) cleanup();
  };
}
