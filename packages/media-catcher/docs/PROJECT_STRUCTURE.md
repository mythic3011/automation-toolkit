# 📂 Project Structure Guide

Complete overview of the Media Catcher project organization.

---

## 🌳 Directory Tree

```
media-catcher/
│
├── src/                          # Source code (ES6 modules)
│   │
│   ├── core/                     # Core functionality & utilities
│   │   ├── config.js            # Configuration constants
│   │   │   ├── CONFIG           # App settings (sizes, timings, patterns)
│   │   │   ├── USELESS_VALUES   # Values to filter during cleaning
│   │   │   └── USERSCRIPT_METADATA # Script header information
│   │   │
│   │   ├── state.js             # Global state management
│   │   │   ├── state            # Application state object
│   │   │   ├── DOM              # Cached DOM element references
│   │   │   └── cacheDOMElements() # Cache DOM for performance
│   │   │
│   │   └── utils.js             # Utility functions
│   │       ├── getPageTitle()   # Extract & sanitize page title
│   │       ├── createFilename() # Generate ISO-formatted filenames
│   │       ├── formatDateTime() # Format dates for display
│   │       ├── generateHash()   # FNV-1a hash algorithm
│   │       ├── debounce()       # Function debouncing
│   │       └── isVTTFormat()    # Detect VTT content
│   │
│   ├── data/                     # Data processing layer
│   │   ├── cleaner.js           # JSON data cleaning
│   │   │   └── cleanJSON()      # Remove useless fields recursively
│   │   │
│   │   ├── downloader.js        # File download functionality
│   │   │   ├── downloadJSON()   # Download JSON files
│   │   │   └── downloadVTT()    # Download VTT files
│   │   │
│   │   └── deduplication.js     # Duplicate detection & memory mgmt
│   │       ├── isDuplicate()    # Check if hash exists
│   │       ├── isTooSmall()     # Check size threshold
│   │       └── enforceRequestLimit() # Memory management
│   │
│   ├── handlers/                 # Business logic layer
│   │   └── response.js          # Main response handling
│   │       └── handleCapturedResponse() # Process captured data
│   │           ├── Size check
│   │           ├── Duplicate check
│   │           ├── Hash generation
│   │           ├── Storage
│   │           ├── Auto-download (optional)
│   │           ├── UI update
│   │           └── Notification
│   │
│   ├── interceptors/             # Network interception layer
│   │   ├── xhr.js               # XMLHttpRequest interception
│   │   │   ├── Override open()
│   │   │   ├── Override send()
│   │   │   ├── Hook onreadystatechange
│   │   │   ├── Hook onload
│   │   │   └── setupXHRInterceptor()
│   │   │
│   │   └── fetch.js             # Fetch API interception
│   │       ├── Override fetch()
│   │       ├── Clone response
│   │       ├── Parse data
│   │       └── setupFetchInterceptor()
│   │
│   ├── ui/                       # User interface layer
│   │   ├── styles.js            # CSS styles
│   │   │   ├── styles           # CSS string with all styles
│   │   │   └── injectStyles()   # Inject into page
│   │   │
│   │   ├── gui.js               # Main GUI logic
│   │   │   ├── createGUI()      # Build all GUI elements
│   │   │   ├── updateUI()       # Refresh UI (debounced)
│   │   │   ├── togglePanel()    # Show/hide panel
│   │   │   ├── toggleAutoDownload()
│   │   │   ├── toggleCleanData()
│   │   │   ├── toggleDeduplication()
│   │   │   ├── clearAllRequests()
│   │   │   ├── makeDraggable()  # Dragging functionality
│   │   │   └── setupPublicAPI() # Expose window.panoptoCatcher
│   │   │
│   │   ├── notifications.js     # Toast notification system
│   │   │   └── showNotification() # Display auto-dismiss toast
│   │   │
│   │   └── dialogs.js           # Modal confirmation dialogs
│   │       └── showConfirmDialog() # Show confirm modal
│   │
│   └── main.js                   # Application entry point
│       ├── Import all modules
│       ├── Setup interceptors
│       ├── Setup public API
│       ├── Initialize GUI
│       └── Handle initialization edge cases
│
├── build/                        # Build system
│   └── build.js                 # Module bundler
│       ├── ModuleBundler class
│       ├── readModule()         # Parse module files
│       ├── resolveImportPath()  # Resolve dependencies
│       ├── processModule()      # Build dependency graph
│       ├── transformModuleContent() # Remove imports/exports
│       └── build()              # Bundle all modules
│
├── dist/                         # Build output (generated)
│   └── media-catcher.user.js    # Final bundled UserScript
│                                # (~42 KB, ready for Tampermonkey)
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # Architecture & design decisions
│   ├── CONTRIBUTING.md          # How to contribute
│   ├── DEVELOPMENT.md           # Development workflow & guide
│   ├── INSTALL.md               # Installation instructions
│   ├── TROUBLESHOOTING.md       # Debugging & common issues
│   ├── PERFORMANCE_IMPROVEMENTS.md # Performance optimizations
│   ├── ZOOM_VTT_SUPPORT.md      # Zoom integration details
│   ├── MODERN_UI_IMPROVEMENTS.md # UI enhancement details
│   └── PROJECT_STRUCTURE.md     # This file
│
├── package.json                  # NPM configuration
│   ├── Scripts: build, watch, lint, format, clean
│   └── Dev dependencies: eslint, prettier, nodemon
│
├── .eslintrc.json               # ESLint configuration
├── .prettierrc.json             # Prettier configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # Project overview & quick start
```

---

## 📦 Module Dependencies

### Dependency Graph

```
main.js
  ├── interceptors/xhr.js
  │   ├── core/config.js
  │   ├── core/utils.js
  │   └── handlers/response.js
  │       ├── core/state.js
  │       ├── core/utils.js
  │       ├── data/deduplication.js
  │       │   ├── core/config.js
  │       │   └── core/state.js
  │       ├── data/downloader.js
  │       │   ├── data/cleaner.js
  │       │   │   ├── core/config.js
  │       │   │   └── core/state.js
  │       │   └── core/state.js
  │       ├── ui/gui.js
  │       │   ├── core/state.js
  │       │   ├── core/config.js
  │       │   ├── core/utils.js
  │       │   ├── data/downloader.js
  │       │   ├── ui/styles.js
  │       │   ├── ui/notifications.js
  │       │   │   └── core/config.js
  │       │   └── ui/dialogs.js
  │       └── ui/notifications.js
  │
  ├── interceptors/fetch.js
  │   └── (same as xhr.js)
  │
  └── ui/gui.js
      └── (as above)
```

### Import Relationships

**Most Imported Modules** (high coupling):
1. `core/config.js` - Used by almost everyone
2. `core/state.js` - Used by data & UI layers
3. `core/utils.js` - Used across all layers

**Isolated Modules** (low coupling):
1. `ui/dialogs.js` - Only imported by `gui.js`
2. `ui/notifications.js` - Only imported by `gui.js` and `response.js`
3. `ui/styles.js` - Only imported by `gui.js`

---

## 🔄 Data Flow

### From Request to Download

```
1. Browser Request
   ↓
2. Interceptor (xhr.js or fetch.js)
   ├─ Detects URL pattern
   ├─ Hooks into response
   └─ Parses data
   ↓
3. Response Handler (handlers/response.js)
   ├─ Calculate size
   ├─ Check: isTooSmall()
   ├─ Check: isDuplicate()
   └─ Create request object
   ↓
4. Data Processing
   ├─ Generate hash (utils.js)
   ├─ Clean data (cleaner.js) if enabled
   └─ Store in state
   ↓
5. Auto-Download (optional)
   ├─ downloadJSON() or
   └─ downloadVTT()
   ↓
6. UI Update (gui.js)
   ├─ Update stats
   ├─ Update request list
   └─ Update badge
   ↓
7. User Notification (notifications.js)
   └─ Show toast message
```

---

## 🏗️ Layer Responsibilities

### Core Layer
**Purpose**: Foundation and shared utilities
**Files**: `config.js`, `state.js`, `utils.js`
**Rules**:
- No dependencies on other layers
- Pure functions (utils.js)
- Immutable constants (config.js)
- Centralized state (state.js)

### Data Layer
**Purpose**: Data transformation and persistence
**Files**: `cleaner.js`, `downloader.js`, `deduplication.js`
**Rules**:
- Depends only on Core layer
- No UI dependencies
- No network dependencies
- Pure data processing

### Handlers Layer
**Purpose**: Business logic orchestration
**Files**: `response.js`
**Rules**:
- Orchestrates data and UI layers
- Contains main business logic
- Calls other layers, doesn't implement details

### Interceptors Layer
**Purpose**: Network request/response interception
**Files**: `xhr.js`, `fetch.js`
**Rules**:
- Depends on Core and Handlers
- No UI dependencies
- Handles browser APIs only

### UI Layer
**Purpose**: User interface and interaction
**Files**: `gui.js`, `styles.js`, `notifications.js`, `dialogs.js`
**Rules**:
- Depends on Core and Data layers
- Contains all DOM manipulation
- Handles user events

---

## 📋 File Sizes

Approximate sizes after build:

```
dist/media-catcher.user.js    ~42 KB  (final bundle)

Source files (unminified):
src/main.js                    ~4 KB
src/core/config.js            ~1 KB
src/core/state.js             ~1 KB
src/core/utils.js             ~2 KB
src/data/cleaner.js           ~2 KB
src/data/downloader.js        ~2 KB
src/data/deduplication.js     ~1 KB
src/handlers/response.js      ~3 KB
src/interceptors/xhr.js       ~5 KB
src/interceptors/fetch.js     ~2 KB
src/ui/gui.js                 ~10 KB
src/ui/styles.js              ~8 KB
src/ui/notifications.js       ~1 KB
src/ui/dialogs.js             ~3 KB
```

---

## 🧩 Adding New Files

### Where to Add New Code

**Configuration/Constants** → `src/core/config.js`
```javascript
export const MY_NEW_CONSTANT = "value";
```

**Utility Function** → `src/core/utils.js`
```javascript
export function myUtility() { ... }
```

**Data Processing** → `src/data/my-processor.js` (new file)
```javascript
export function processData(data) { ... }
```

**Business Logic** → `src/handlers/my-handler.js` (new file)
```javascript
export function handleSomething() { ... }
```

**Network Layer** → `src/interceptors/` (rare)
```javascript
// Only if adding new interception mechanism
```

**UI Component** → `src/ui/my-component.js` (new file)
```javascript
export function showMyComponent() { ... }
```

### Import the New Module

**In appropriate file** (e.g., `main.js`, `gui.js`):
```javascript
import { myUtility } from "./core/utils.js";
import { processData } from "./data/my-processor.js";
```

**Build will automatically include it**:
```bash
npm run build
```

---

## 🔍 Finding Code

### "Where should I look for...?"

**Config values**
→ `src/core/config.js`

**State/data storage**
→ `src/core/state.js`

**Date/time formatting**
→ `src/core/utils.js`

**Duplicate detection**
→ `src/data/deduplication.js`

**File downloads**
→ `src/data/downloader.js`

**JSON cleaning**
→ `src/data/cleaner.js`

**Request capture**
→ `src/interceptors/xhr.js` and `fetch.js`

**Main business logic**
→ `src/handlers/response.js`

**GUI creation**
→ `src/ui/gui.js`

**Styles**
→ `src/ui/styles.js`

**Notifications**
→ `src/ui/notifications.js`

**Confirmation dialogs**
→ `src/ui/dialogs.js`

**Initialization**
→ `src/main.js`

**Build process**
→ `build/build.js`

---

## 🎯 Best Practices

### File Organization

1. **One responsibility per file**
   - ✅ Good: `downloader.js` only handles downloads
   - ❌ Bad: `utils.js` handles downloads, cleaning, and UI

2. **Clear naming**
   - ✅ Good: `handleCapturedResponse()`
   - ❌ Bad: `process()`, `doStuff()`

3. **Logical grouping**
   - Keep related functions in same file
   - Group by feature, not by type

### Import Organization

```javascript
// 1. External dependencies (none in this project)

// 2. Core imports
import { CONFIG } from "../core/config.js";
import { state } from "../core/state.js";

// 3. Data imports
import { cleanJSON } from "../data/cleaner.js";

// 4. Handler imports
import { handleCapturedResponse } from "../handlers/response.js";

// 5. UI imports
import { updateUI } from "../ui/gui.js";
```

### Export Organization

```javascript
// Named exports (preferred)
export function myFunction() { ... }
export const MY_CONSTANT = "value";

// Default exports (avoid)
// export default MyClass;
```

---

## 📊 Statistics

- **Total modules**: 14
- **Total source files**: 15 (14 modules + build script)
- **Lines of code**: ~1,500
- **Build output**: ~1,400 lines (with comments)
- **Build time**: < 1 second
- **Bundle size**: ~42 KB

---

## 🔗 Related Documentation

- [Architecture](ARCHITECTURE.md) - Design decisions
- [Development](DEVELOPMENT.md) - How to develop
- [Contributing](CONTRIBUTING.md) - How to contribute

---

**Structure designed for clarity and maintainability** 🎯

