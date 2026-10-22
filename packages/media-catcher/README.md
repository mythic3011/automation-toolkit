# 🎯 Media Catcher - Panopto & Zoom UserScript

A powerful, modular UserScript for capturing and downloading media data from Panopto and Zoom platforms. Features a modern GUI, smart deduplication, data cleaning, and support for both JSON (Panopto) and VTT (Zoom) formats.

![Version](https://img.shields.io/badge/version-2.4-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## ✨ Features

### Core Functionality
- 📥 **Automatic Capture** - Intercepts XHR and Fetch requests automatically
- 🎯 **Dual Platform Support** - Works with Panopto JSON and Zoom VTT formats
- 💾 **Smart Download** - Auto or manual download with customizable options
- 🧹 **Data Cleaning** - Removes null, false, 0, empty UUIDs, and default dates
- 🔁 **Deduplication** - Filters duplicate packets using FNV-1a hashing
- 📏 **Size Filtering** - Skips small/meaningless packets (<100 bytes)

### User Interface
- 🎨 **Modern GUI** - Beautiful, draggable control panel
- 📊 **Real-time Stats** - Track captured and downloaded requests
- 🔔 **Notifications** - Non-blocking toast notifications
- ⚙️ **Toggles** - Easy control over auto-download, cleaning, and deduplication
- 👁️ **Data Viewer** - Inspect captured data in console

### Performance
- ⚡ **Optimized** - Debounced UI updates, DOM caching, Set-based lookups
- 🧠 **Memory Management** - Automatic request limit enforcement (50 max)
- 🎯 **FNV-1a Hashing** - Fast duplicate detection
- 🖼️ **RequestAnimationFrame** - Smooth animations

---

## 🚀 Quick Start

### Installation

1. **Install Tampermonkey**
   - [Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)
   - [Edge](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd)

2. **Install the UserScript**
   - Download `dist/media-catcher.user.js`
   - Open Tampermonkey dashboard
   - Click "Install" when prompted

3. **Use the Script**
   - Visit a Panopto or Zoom recording page
   - Look for the 📥 button in the bottom-right corner
   - Play the video to start capturing

---

## 📦 Development Setup

### Prerequisites
- Node.js >= 18.0.0
- npm

### Install Dependencies
```bash
cd media-catcher
npm install
```

### Build the UserScript
```bash
npm run build
```

### Development Workflow
```bash
# Watch for changes and rebuild automatically
npm run watch

# Run bundle smoke tests
npm test

# Lint code
npm run lint:all

# Check formatting
npm run format:check

# Format code
npm run format

# Clean build artifacts
npm run clean
```

---

## 🏗️ Project Structure

```
media-catcher/
├── src/                      # Source code (modular)
│   ├── core/                 # Core functionality
│   │   ├── config.js         # Configuration constants
│   │   ├── state.js          # State management
│   │   └── utils.js          # Utility functions
│   ├── data/                 # Data processing
│   │   ├── cleaner.js        # JSON cleaning logic
│   │   ├── downloader.js     # File download functions
│   │   └── deduplication.js  # Duplicate detection
│   ├── handlers/             # Request handlers
│   │   └── response.js       # Response processing
│   ├── interceptors/         # Network interception
│   │   ├── xhr.js            # XMLHttpRequest interceptor
│   │   └── fetch.js          # Fetch API interceptor
│   ├── ui/                   # User interface
│   │   ├── gui.js            # GUI creation & management
│   │   ├── styles.js         # CSS styles
│   │   ├── notifications.js  # Toast notifications
│   │   └── dialogs.js        # Confirmation dialogs
│   └── main.js               # Entry point
├── build/                    # Build scripts
│   └── build.js              # Module bundler
├── dist/                     # Built UserScript (generated)
│   └── media-catcher.user.js # Final bundled script
├── docs/                     # Documentation
│   ├── INSTALL.md            # Installation guide
│   ├── TROUBLESHOOTING.md    # Debugging help
│   ├── PERFORMANCE_IMPROVEMENTS.md
│   ├── ZOOM_VTT_SUPPORT.md
│   ├── MODERN_UI_IMPROVEMENTS.md
│   ├── ARCHITECTURE.md       # Architecture overview
│   └── CONTRIBUTING.md       # Contribution guide
├── package.json              # NPM configuration
├── .eslintrc.json            # ESLint configuration
├── .prettierrc.json          # Prettier configuration
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🔧 Configuration

### Modifying Constants

Edit `src/core/config.js` to adjust:

```javascript
export const CONFIG = {
  MIN_SIZE_BYTES: 100,           // Minimum response size
  MAX_REQUESTS_STORED: 50,       // Maximum stored requests
  UPDATE_DEBOUNCE_MS: 100,       // UI update delay
  NOTIFICATION_DURATION_MS: 2000,// Notification display time
  PANOPTO_URL_PATTERN: "...",    // URL pattern to match
  ZOOM_VTT_PATTERN: "...",       // Zoom VTT pattern
};
```

### Customizing UI Styles

Edit `src/ui/styles.js` to modify colors, sizes, and animations.

---

## 📖 Usage

### Console Commands

```javascript
// Show current status
panoptoCatcher.status();

// Show help
panoptoCatcher.help();

// Show panel programmatically
panoptoCatcher.showPanel();

// Download specific request
panoptoCatcher.download(0);

// View request data in console
panoptoCatcher.view(0);
```

### GUI Controls

- **📥 Floating Button** - Click to toggle the control panel
- **Auto Download** - Automatically download captured requests
- **Clean Useless Fields** - Remove null/empty values from JSON
- **Filter Duplicates** - Skip duplicate responses
- **💾 Download** - Manually download a captured request
- **👁️ View** - Inspect request data in console
- **🗑️ Clear All** - Remove all captured requests

---

## 🎨 Architecture

### Module Organization

The project follows a modular architecture for better maintainability:

- **Core** - Foundation (config, state, utilities)
- **Data** - Data processing (cleaning, downloading, deduplication)
- **Handlers** - Business logic (response handling)
- **Interceptors** - Network layer (XHR, Fetch)
- **UI** - Presentation layer (GUI, notifications, dialogs)

### Build Process

1. **Source Files** - Write modular ES6 code with imports/exports
2. **Build Script** - Bundles all modules into a single file
3. **Transform** - Removes imports/exports, wraps in IIFE
4. **Output** - Single UserScript file with metadata

### Data Flow

```
Request Intercepted (XHR/Fetch)
         ↓
Response Handler (response.js)
         ↓
Deduplication Check (deduplication.js)
         ↓
Size Check (deduplication.js)
         ↓
Data Cleaning (cleaner.js)
         ↓
Auto Download? (downloader.js)
         ↓
Update GUI (gui.js)
         ↓
Show Notification (notifications.js)
```

---

## 🧪 Testing

### Manual Testing

1. Build the script: `npm run build`
2. Install `dist/media-catcher.user.js` in Tampermonkey
3. Visit test URLs:
   - **Panopto**: `https://polyu.ap.panopto.com/Panopto/Pages/Viewer.aspx?id=...`
   - **Zoom**: `https://polyu.zoom.us/rec/play/...`
4. Open browser console (F12)
5. Check for logs: `[Media Catcher]`
6. Verify GUI appears (📥 button)

### Debug Mode

Enable verbose logging:
```javascript
// In console
panoptoCatcher.status();
```

---

## 🐛 Troubleshooting

### GUI Not Appearing

1. Check console for errors
2. Run `panoptoCatcher.status()`
3. Verify URL matches @match patterns
4. Try `panoptoCatcher.showPanel()`

### Requests Not Captured

1. Check Network tab (F12)
2. Verify POST to `DeliveryInfo.aspx` (Panopto)
3. Verify GET to `/rec/play/vtt` (Zoom)
4. Check console for `🎯 REQUEST INTERCEPTED`

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more details.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make changes to `src/` files
4. Test with `npm run build`
5. Run linter: `npm run lint`
6. Format code: `npm run format`
7. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

- **Author**: You
- **Version**: 2.4 (Modular Architecture)
- **Platforms**: Panopto, Zoom
- **Technologies**: JavaScript (ES6), UserScript, Tampermonkey

---

## 📞 Support

- **Issues**: [GitHub Issues](your-repo-url/issues)
- **Documentation**: See [docs/](docs/) folder
- **Console Help**: Type `panoptoCatcher.help()`

---

## 🔄 Changelog

### Version 2.4 (Current)
- ✨ Modular architecture with ES6 modules
- 🏗️ Build system for bundling
- 🎨 Improved code organization
- 📚 Comprehensive documentation
- 🧪 Development tooling (ESLint, Prettier)

### Version 2.3
- ✨ Zoom VTT support
- 📝 VTT file downloads

### Version 2.2
- ⚡ Performance optimizations
- 🧠 Memory management
- 🎯 FNV-1a hashing

### Version 2.1
- 🎨 Modern UI components
- 🔔 Toast notifications
- ⚠️ Confirmation dialogs

### Version 2.0
- 🎨 GUI with draggable panel
- 🧹 Data cleaning
- 🔁 Deduplication

### Version 1.0
- 📥 Basic XHR interception
- 💾 JSON download

---

## 🎯 Roadmap

- [ ] Add unit tests
- [ ] Support more platforms
- [ ] Export/import settings
- [ ] Batch download
- [ ] Search/filter captured requests
- [ ] Export history as CSV/JSON

---

**Built with ❤️ for better media management**

