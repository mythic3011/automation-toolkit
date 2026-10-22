# 🛠️ Development Guide

Complete guide for developing and extending Media Catcher.

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd media-catcher
npm install

# Start development
npm run watch   # Auto-rebuild on changes
```

---

## 📁 Project Structure

```
media-catcher/
├── src/                    # Source code (edit here)
│   ├── core/              # Foundation
│   │   ├── config.js      # Constants & configuration
│   │   ├── state.js       # Global state management
│   │   └── utils.js       # Utility functions
│   ├── data/              # Data processing
│   │   ├── cleaner.js     # JSON cleaning
│   │   ├── downloader.js  # File downloads
│   │   └── deduplication.js # Duplicate detection
│   ├── handlers/          # Business logic
│   │   └── response.js    # Response handling
│   ├── interceptors/      # Network layer
│   │   ├── xhr.js         # XHR interception
│   │   └── fetch.js       # Fetch interception
│   ├── ui/                # User interface
│   │   ├── gui.js         # Main GUI
│   │   ├── styles.js      # CSS styles
│   │   ├── notifications.js # Toast messages
│   │   └── dialogs.js     # Confirmation dialogs
│   └── main.js            # Entry point
├── build/                 # Build tools
│   └── build.js           # Module bundler
├── dist/                  # Build output (generated)
│   └── media-catcher.user.js # Final UserScript
├── docs/                  # Documentation
└── package.json           # NPM configuration
```

---

## 🔧 Development Workflow

### 1. Make Changes

Edit files in `src/` directory. Each module has a specific purpose.

### 2. Build

```bash
# One-time build
npm run build

# Watch mode (recommended)
npm run watch
```

### 3. Install in Browser

1. Open `dist/media-catcher.user.js`
2. Copy entire contents
3. Open Tampermonkey dashboard
4. Click "Create new script"
5. Replace default with copied code
6. Save (Ctrl+S)

### 4. Test

1. Visit Panopto or Zoom page
2. Open console (F12)
3. Look for `[Media Catcher]` logs
4. Verify GUI appears (📥 button)
5. Test functionality

### 5. Debug

```javascript
// In browser console:
panoptoCatcher.status();  // Check status
panoptoCatcher.help();    // Show help
```

---

## 📦 Build System

### How It Works

The build script (`build/build.js`) is a simple module bundler:

1. **Entry Point**: Reads `src/main.js`
2. **Dependency Graph**: Recursively resolves all imports
3. **Processing**: Parses each module
4. **Transformation**: Removes import/export statements
5. **Bundling**: Concatenates all code
6. **Output**: Writes to `dist/media-catcher.user.js`

### Build Output

```javascript
// ==UserScript==
// @name         Media Catcher
// ... metadata ...
// ==/UserScript==

(function () {
  "use strict";

  // ==================== Module: core/config.js ====================
  const CONFIG = { ... };

  // ==================== Module: core/state.js ====================
  const state = { ... };

  // ... all other modules ...

  // ==================== Module: main.js ====================
  // Initialization code
})();
```

### Why This Approach?

- **Simple**: No complex bundler (Webpack/Rollup) needed
- **Transparent**: Easy to understand and debug
- **Reliable**: Minimal dependencies
- **Fast**: Quick builds

---

## 🧩 Adding New Features

### Example: Add New Platform Support

Let's add support for "Platform X":

#### 1. Update Config

**File**: `src/core/config.js`

```javascript
export const CONFIG = {
  // ... existing config ...
  PLATFORMX_URL_PATTERN: "/api/media/data",
};
```

#### 2. Update Interceptor

**File**: `src/interceptors/xhr.js`

```javascript
// Add detection
const isPlatformXRequest =
  xhr._method === "GET" &&
  xhr._url &&
  xhr._url.includes(CONFIG.PLATFORMX_URL_PATTERN);

// Add to if condition
if (isPanoptoRequest || isZoomVTTRequest || isPlatformXRequest) {
  // ... handle request
}
```

#### 3. Update Handler

**File**: `src/handlers/response.js`

```javascript
// Add content type handling
if (contentType === "platformx") {
  // Process Platform X data
}
```

#### 4. Test

```bash
npm run build
# Install in browser and test
```

---

## 🎨 UI Customization

### Changing Colors

**File**: `src/ui/styles.js`

```javascript
// Current gradient
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

// Change to blue
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

// Change to green
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
```

### Adding UI Component

**File**: `src/ui/my-component.js`

```javascript
/**
 * My new component
 */

export function showMyComponent(message) {
  const component = document.createElement("div");
  component.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  `;
  component.textContent = message;
  document.body.appendChild(component);

  // Auto-remove after 3 seconds
  setTimeout(() => component.remove(), 3000);
}
```

**Use it**: Import in `src/main.js` or other modules

```javascript
import { showMyComponent } from "./ui/my-component.js";

showMyComponent("Hello, World!");
```

---

## 🔍 Debugging

### Console Logging

All modules use consistent logging:

```javascript
console.log("[Media Catcher] Message here");
console.error("[Media Catcher] Error:", error);
```

### Debug Commands

```javascript
// Show status
panoptoCatcher.status();

// Show help
panoptoCatcher.help();

// Show panel
panoptoCatcher.showPanel();

// Check state
console.log(window.panoptoCatcher);
```

### Common Issues

**GUI not appearing**:
```javascript
// Check if script loaded
panoptoCatcher.status();

// Force show panel
panoptoCatcher.showPanel();

// Check for errors
// Look in console for errors
```

**Requests not captured**:
```javascript
// Check Network tab
// Filter by: DeliveryInfo.aspx (Panopto) or vtt (Zoom)

// Check console for:
// "🎯 REQUEST INTERCEPTED!"
```

**Build errors**:
```bash
# Check for syntax errors
npm run lint

# Clean and rebuild
npm run clean
npm run build
```

---

## 🧪 Testing

### Manual Testing Checklist

#### Basic Functionality
- [ ] Script loads without errors
- [ ] GUI appears (📥 button)
- [ ] Panel opens when clicking button
- [ ] Panel is draggable
- [ ] Panel closes when clicking X

#### Feature Testing
- [ ] Auto-download toggle works
- [ ] Clean data toggle works
- [ ] Deduplication toggle works
- [ ] Stats update correctly
- [ ] Request list shows captured items
- [ ] Download button works
- [ ] View button logs to console
- [ ] Clear all button works (with confirmation)

#### Platform Testing
- [ ] Panopto JSON capture works
- [ ] Zoom VTT capture works
- [ ] Files download with correct names
- [ ] Duplicate requests are filtered
- [ ] Small requests are filtered

#### Edge Cases
- [ ] Works on page reload
- [ ] Works on SPA navigation
- [ ] Handles multiple requests rapidly
- [ ] Memory limit enforcement works (50+ requests)
- [ ] Works with ad blockers enabled
- [ ] Works with other UserScripts

### Test URLs

**Panopto**:
- `https://polyu.ap.panopto.com/Panopto/Pages/Viewer.aspx?id=...`

**Zoom**:
- `https://polyu.zoom.us/rec/play/...`

---

## 📊 Performance Profiling

### Measuring Performance

```javascript
// In browser console:

// 1. Profile UI update
console.time("updateUI");
panoptoCatcher.updateUI();
console.timeEnd("updateUI");

// 2. Profile hash generation
console.time("generateHash");
generateHash(largeObject);
console.timeEnd("generateHash");

// 3. Profile data cleaning
console.time("cleanJSON");
cleanJSON(dirtyData);
console.timeEnd("cleanJSON");
```

### Performance Targets

- UI update: < 10ms
- Hash generation: < 1ms
- Data cleaning: < 5ms
- File download: < 100ms

---

## 🔐 Security

### Best Practices

1. **No eval()**: Never use `eval()` or `new Function()`
2. **Sanitize input**: Always validate/sanitize user input
3. **No XSS**: Escape HTML when setting `innerHTML`
4. **No external scripts**: Don't load external resources
5. **Minimal permissions**: Keep `@grant` to minimum

### Safe HTML Insertion

**Bad**:
```javascript
element.innerHTML = userInput; // XSS risk!
```

**Good**:
```javascript
element.textContent = userInput; // Safe
// or
element.innerHTML = escapeHTML(userInput); // Sanitized
```

---

## 📈 Optimization Tips

### 1. Minimize DOM Access

**Bad**:
```javascript
function update() {
  document.getElementById("stat").textContent = count;
  document.getElementById("stat2").textContent = count2;
  // ... repeated DOM queries
}
```

**Good**:
```javascript
const DOM = {
  stat: document.getElementById("stat"),
  stat2: document.getElementById("stat2"),
};

function update() {
  DOM.stat.textContent = count;
  DOM.stat2.textContent = count2;
}
```

### 2. Debounce Frequent Updates

**Bad**:
```javascript
// Called on every keystroke
input.addEventListener("input", expensiveOperation);
```

**Good**:
```javascript
const debounced = debounce(expensiveOperation, 300);
input.addEventListener("input", debounced);
```

### 3. Use Set for Lookups

**Bad** (O(n)):
```javascript
const hashes = [];
if (hashes.includes(hash)) { ... }
```

**Good** (O(1)):
```javascript
const hashes = new Set();
if (hashes.has(hash)) { ... }
```

---

## 📚 Resources

### Learning
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [ES6 Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [UserScript Documentation](https://www.tampermonkey.net/documentation.php)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)

### Project Docs
- [README](../README.md)
- [Architecture](ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

## 💡 Tips & Tricks

### 1. Use Watch Mode
```bash
npm run watch
# Now edit files and they auto-rebuild
```

### 2. Console Shortcuts
```javascript
// Alias for convenience
const mc = panoptoCatcher;
mc.status();
mc.help();
```

### 3. Quick Reload
- Make changes
- Build (auto if watching)
- Just refresh browser page (if using file:// URL)
- Or re-save in Tampermonkey editor

### 4. Inspect State
```javascript
// Access internal state (for debugging)
// Note: Not officially exposed, may change
console.log(window.panoptoCatcher);
```

---

## ❓ FAQ

**Q: Why not use Webpack/Rollup?**
A: Simplicity. Our custom bundler is < 200 lines and does exactly what we need.

**Q: Can I use TypeScript?**
A: Not currently, but it's on the roadmap. You can contribute a TS setup!

**Q: How do I add a new module?**
A: Create file in `src/`, add exports, import where needed. Build script handles the rest.

**Q: The build is slow?**
A: It shouldn't be. Usually < 1 second. Check for large files or circular imports.

**Q: Can I use async/await?**
A: Yes! Modern browsers support it.

---

**Happy Developing! 🚀**

Questions? Open an issue with "Question" label.

