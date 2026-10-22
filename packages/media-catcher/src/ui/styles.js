/**
 * CSS styles for the GUI
 * Returns the styles as a string (lazy-loaded to avoid minification issues)
 */

export function getStyles() {
  return `
  #panopto-catcher-panel {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 400px;
    max-height: 600px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    z-index: 999999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: none;
    overflow: hidden;
  }
  
  #panopto-catcher-panel.visible {
    display: block;
    animation: slideIn 0.3s ease-out;
  }
  
  @keyframes slideIn {
    from { transform: translateX(450px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  #panopto-catcher-header {
    background: rgba(0,0,0,0.2);
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: move;
    user-select: none;
  }
  
  #panopto-catcher-header h3 {
    margin: 0;
    color: white;
    font-size: 16px;
    font-weight: 600;
  }
  
  #panopto-catcher-close {
    background: rgba(255,255,255,0.2);
    border: none;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    transition: all 0.2s;
  }
  
  #panopto-catcher-close:hover {
    background: rgba(255,255,255,0.3);
    transform: rotate(90deg);
  }
  
  #panopto-catcher-body {
    background: white;
    padding: 20px;
    max-height: 500px;
    overflow-y: auto;
  }
  
  .catcher-control {
    margin-bottom: 20px;
  }
  
  .catcher-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f7f9fc;
    border-radius: 8px;
    margin-bottom: 10px;
  }
  
  .catcher-toggle label {
    font-weight: 500;
    color: #333;
    font-size: 14px;
  }
  
  .toggle-switch {
    position: relative;
    width: 50px;
    height: 26px;
    background: #ccc;
    border-radius: 13px;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  .toggle-switch.active {
    background: #667eea;
  }
  
  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: transform 0.3s;
  }
  
  .toggle-switch.active::after {
    transform: translateX(24px);
  }
  
  .catcher-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
  }
  
  .stat-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
  }
  
  .stat-value {
    font-size: 24px;
    font-weight: bold;
    display: block;
  }
  
  .stat-label {
    font-size: 12px;
    opacity: 0.9;
    margin-top: 4px;
    display: block;
  }
  
  .requests-list {
    max-height: 250px;
    overflow-y: auto;
  }
  
  .request-item {
    background: #f7f9fc;
    border-left: 4px solid #667eea;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 6px;
    font-size: 13px;
  }
  
  .request-time {
    color: #666;
    font-size: 11px;
    margin-bottom: 6px;
  }
  
  .request-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
  
  .btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: #667eea;
    color: white;
  }
  
  .btn-primary:hover {
    background: #5568d3;
    transform: translateY(-1px);
  }
  
  .btn-secondary {
    background: #e0e7ff;
    color: #667eea;
  }
  
  .btn-secondary:hover {
    background: #c7d2fe;
  }
  
  .btn-clear {
    background: #fee;
    color: #e53e3e;
    width: 100%;
    margin-top: 10px;
  }
  
  .btn-clear:hover {
    background: #fdd;
  }
  
  #panopto-catcher-toggle-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    z-index: 999998;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  #panopto-catcher-toggle-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  }
  
  .badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background: #e53e3e;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: bold;
    min-width: 20px;
    text-align: center;
  }
  
  .empty-state {
    text-align: center;
    padding: 30px;
    color: #999;
  }
  
  .empty-state-icon {
    font-size: 48px;
    margin-bottom: 10px;
  }
`;
}

/**
 * Inject styles into the page
 */
export function injectStyles() {
  console.log("[Media Catcher] Injecting styles...");
  const styleSheet = document.createElement("style");
  styleSheet.textContent = getStyles();
  styleSheet.id = "panopto-catcher-styles";
  (document.head || document.documentElement).appendChild(styleSheet);
  console.log("[Media Catcher] Styles injected successfully");
}
