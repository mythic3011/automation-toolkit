# 🏗️ Architecture Documentation

## Overview

Media Catcher is built using a modular architecture that separates concerns into distinct layers. This document explains the design decisions, module responsibilities, and data flow.

---

## 🎯 Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- **Core**: Foundation and shared utilities
- **Data**: Data processing and transformation
- **Handlers**: Business logic
- **Interceptors**: Network layer
- **UI**: Presentation layer

### 2. **Modularity**
- Source code split into ES6 modules
- Clear import/export boundaries
- Reusable components
- Easy to test and maintain

### 3. **Performance**
- Debounced UI updates
- DOM caching
- Set-based lookups (O(1))
- RequestAnimationFrame for animations
- Memory management with request limits

### 4. **Single Responsibility**
Each file has one job:
- `config.js` - Constants only
- `state.js` - State management only
- `downloader.js` - Download logic only

---

## 📦 Module Structure

### Core Layer (`src/core/`)

#### `config.js`
**Purpose**: Centralized configuration constants

**Exports**:
```javascript
CONFIG                 // Application constants
USELESS_VALUES         // Values to filter during cleaning
USERSCRIPT_METADATA    // UserScript header metadata
```

**Why separate?**
- Single source of truth for configuration
- Easy to modify settings
- No magic numbers in code

#### `state.js`
**Purpose**: Global state management and DOM caching

**Exports**:
```javascript
state                  // Global application state
DOM                    // Cached DOM elements
cacheDOMElements()     // Function to cache DOM refs
```

**State structure**:
```javascript
{
  autoDownload: boolean,
  cleanData: boolean,
  deduplication: boolean,
  minSize: number,
  capturedRequests: Array,
  isPanelVisible: boolean,
  requestHashes: Set
}
```

**Why separate?**
- Central state management
- Avoid prop drilling
- Performance optimization with DOM cache

#### `utils.js`
**Purpose**: Shared utility functions

**Functions**:
- `getPageTitle()` - Safe title extraction
- `createFilename()` - ISO-formatted filenames
- `formatDateTime()` - Display formatting
- `generateHash()` - FNV-1a hash generation
- `debounce()` - Function debouncing
- `isVTTFormat()` - VTT format detection

**Why separate?**
- DRY (Don't Repeat Yourself)
- Testable pure functions
- Reusable across modules

---

### Data Layer (`src/data/`)

#### `cleaner.js`
**Purpose**: JSON data cleaning

**Exports**:
- `cleanJSON(data)` - Remove useless fields

**Algorithm**:
1. Check if cleaning enabled
2. Recursively traverse object/array
3. Filter out values in USELESS_VALUES set
4. Remove empty nested objects
5. Return cleaned data

**Why separate?**
- Complex logic deserves own file
- Easy to modify cleaning rules
- Testable in isolation

#### `downloader.js`
**Purpose**: File download functionality

**Exports**:
- `downloadJSON(data, filename)` - Download JSON
- `downloadVTT(data, filename)` - Download VTT

**How it works**:
1. Create Blob with correct MIME type
2. Generate Object URL
3. Create temporary `<a>` element
4. Trigger click
5. Clean up

**Why separate?**
- Different formats need different handling
- Encapsulates download logic
- Easy to add new formats

#### `deduplication.js`
**Purpose**: Duplicate detection and memory management

**Exports**:
- `isDuplicate(hash)` - Check if hash exists
- `isTooSmall(size)` - Check size threshold
- `enforceRequestLimit()` - Manage memory

**Why separate?**
- Focused on one concern
- Performance-critical code
- Easy to tune parameters

---

### Handlers Layer (`src/handlers/`)

#### `response.js`
**Purpose**: Main business logic for handling captured responses

**Exports**:
- `handleCapturedResponse(data, contentType)` - Process captured data

**Flow**:
```
1. Calculate response size
2. Check if too small → skip
3. Generate hash
4. Check if duplicate → skip
5. Create request object
6. Add to state
7. Enforce request limit
8. Auto-download if enabled
9. Update UI
10. Show notification
```

**Why separate?**
- Central business logic
- Easy to understand flow
- Single place to modify behavior

---

### Interceptors Layer (`src/interceptors/`)

#### `xhr.js`
**Purpose**: XMLHttpRequest interception

**How it works**:
1. Save original `open` and `send` methods
2. Override with custom implementations
3. Detect target URLs (Panopto/Zoom)
4. Hook into `onreadystatechange` and `onload`
5. Parse response
6. Call `handleCapturedResponse`

**Why separate?**
- Isolates XHR-specific code
- Easier to debug network issues
- Clear responsibility

#### `fetch.js`
**Purpose**: Fetch API interception

**How it works**:
1. Save original `fetch`
2. Override with custom implementation
3. Detect target URLs
4. Clone response (to read without consuming)
5. Parse response
6. Call `handleCapturedResponse`

**Why separate?**
- Modern apps use Fetch instead of XHR
- Different API requires different handling
- Backup if XHR doesn't catch request

---

### UI Layer (`src/ui/`)

#### `styles.js`
**Purpose**: CSS styles for all UI components

**Exports**:
- `styles` - CSS string
- `injectStyles()` - Inject styles into page

**Why separate?**
- Keeps CSS out of JavaScript logic
- Easy to modify styling
- Can be extracted to CSS file later

#### `notifications.js`
**Purpose**: Toast notification system

**Exports**:
- `showNotification(message)` - Display toast

**Features**:
- Non-blocking
- Auto-dismiss (2 seconds)
- Smooth animations (requestAnimationFrame)
- Purple gradient design

**Why separate?**
- Reusable notification system
- Could be used by other modules
- Encapsulates animation logic

#### `dialogs.js`
**Purpose**: Modern confirmation dialogs

**Exports**:
- `showConfirmDialog(message, onConfirm)` - Show modal

**Features**:
- Modal overlay
- ESC key support
- Click outside to dismiss
- Hover effects
- Callback-based

**Why separate?**
- Replaces native `confirm()`
- Reusable across app
- Complex DOM manipulation

#### `gui.js`
**Purpose**: Main GUI creation and management

**Exports**:
- `createGUI()` - Build GUI elements
- `updateUI()` - Refresh UI (debounced)
- `togglePanel()` - Show/hide panel
- `toggleAutoDownload()` - Toggle setting
- `toggleCleanData()` - Toggle setting
- `toggleDeduplication()` - Toggle setting
- `clearAllRequests()` - Clear all
- `setupPublicAPI()` - Expose window.panoptoCatcher

**Why separate?**
- Complex UI logic
- Many event handlers
- Public API exposure
- Draggable functionality

---

### Entry Point (`src/main.js`)

**Purpose**: Application initialization

**Responsibilities**:
1. Import all necessary modules
2. Install interceptors
3. Setup public API
4. Initialize GUI when DOM ready
5. Handle multiple initialization scenarios

**Why needed?**
- Single entry point
- Clear initialization order
- Handles edge cases (SPA navigation)

---

## 🔄 Data Flow

### Request Capture Flow

```
┌─────────────────────────────────────────────────┐
│  1. XHR/Fetch Request Made                      │
│     (User plays video)                          │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  2. Interceptor Catches Request                 │
│     (interceptors/xhr.js or fetch.js)           │
│     - Checks URL pattern                        │
│     - Hooks into response handler               │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  3. Response Received                           │
│     - Parse JSON or Text                        │
│     - Detect content type                       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  4. handleCapturedResponse()                    │
│     (handlers/response.js)                      │
│     - Calculate size                            │
│     - Check filters (size, duplicates)          │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  5. Data Processing                             │
│     - Generate hash (utils.js)                  │
│     - Clean data (data/cleaner.js)              │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  6. Storage                                     │
│     - Add to state.capturedRequests             │
│     - Add hash to state.requestHashes           │
│     - Enforce request limit                     │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  7. Auto-Download (Optional)                    │
│     (data/downloader.js)                        │
│     - downloadJSON() or downloadVTT()           │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  8. UI Update                                   │
│     (ui/gui.js)                                 │
│     - Update stats                              │
│     - Update request list                       │
│     - Update badge count                        │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  9. Notification                                │
│     (ui/notifications.js)                       │
│     - Show toast message                        │
│     - Auto-dismiss after 2s                     │
└─────────────────────────────────────────────────┘
```

---

## 🔨 Build Process

### Source to Distribution

```
┌──────────────────────────────────────────────────┐
│  1. Source Files (src/)                          │
│     - 14 modular ES6 files                       │
│     - Import/export statements                   │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  2. Build Script (build/build.js)                │
│     - Read entry point (main.js)                 │
│     - Recursively resolve imports                │
│     - Build dependency graph                     │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  3. Module Processing                            │
│     - Parse import statements                    │
│     - Extract exports                            │
│     - Topological sort (dependencies first)      │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  4. Transformation                               │
│     - Remove import statements                   │
│     - Remove export keywords                     │
│     - Preserve code logic                        │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  5. Bundling                                     │
│     - Add UserScript metadata header             │
│     - Wrap in IIFE (strict mode)                 │
│     - Concatenate all modules                    │
│     - Add module separators (comments)           │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  6. Output (dist/media-catcher.user.js)          │
│     - Single file (~42 KB)                       │
│     - Ready for Tampermonkey installation        │
└──────────────────────────────────────────────────┘
```

---

## 🧠 Memory Management

### Request Storage Strategy

```javascript
// Maximum stored requests
CONFIG.MAX_REQUESTS_STORED = 50

// Storage structure
state.capturedRequests = [
  {
    timestamp: Date,
    data: Object|String,
    hash: String,
    size: Number,
    contentType: String,
    downloaded: Boolean
  },
  // ... up to 50 items
]

// Hash lookup (for O(1) duplicate check)
state.requestHashes = Set([
  "hash1",
  "hash2",
  // ... up to 50 hashes
])
```

### Memory Limit Enforcement

```javascript
function enforceRequestLimit() {
  if (state.capturedRequests.length > MAX_REQUESTS_STORED) {
    const removed = state.capturedRequests.shift(); // Remove oldest
    state.requestHashes.delete(removed.hash);       // Remove from Set
  }
}
```

**Why?**
- Prevents memory leaks
- FIFO (First In, First Out) strategy
- Keeps most recent captures
- Automatic cleanup

---

## ⚡ Performance Optimizations

### 1. **Debounced UI Updates**
```javascript
const updateUI = debounce(updateUIInternal, 100);
```
- Prevents excessive DOM manipulation
- Batches updates within 100ms window
- Smoother user experience

### 2. **DOM Caching**
```javascript
const DOM = {
  panel: null,
  toggleBtn: null,
  // ... cached references
};
```
- Query DOM once, reuse many times
- Avoid repeated `getElementById()` calls
- Significant performance gain

### 3. **Set-based Duplicate Detection**
```javascript
state.requestHashes = new Set();
// O(1) lookup vs O(n) array search
```

### 4. **FNV-1a Hashing**
- Fast, simple hash algorithm
- Good distribution
- Lightweight implementation

### 5. **RequestAnimationFrame**
```javascript
requestAnimationFrame(() => {
  // Smooth animations
});
```
- Browser-optimized timing
- 60 FPS animations
- No jank

---

## 🎨 UI Architecture

### Component Hierarchy

```
Window
 └─ Floating Button (📥)
     └─ Badge (count)
 └─ Control Panel (draggable)
     ├─ Header
     │   ├─ Title
     │   └─ Close Button
     └─ Body
         ├─ Controls
         │   ├─ Auto Download Toggle
         │   ├─ Clean Data Toggle
         │   └─ Deduplication Toggle
         ├─ Stats
         │   ├─ Captured Count
         │   └─ Downloaded Count
         ├─ Request List
         │   └─ Request Items (dynamic)
         │       ├─ Timestamp
         │       ├─ Info (type, size)
         │       └─ Actions
         │           ├─ Download Button
         │           └─ View Button
         └─ Clear All Button
 └─ Notifications (toast, temporary)
 └─ Dialogs (modal overlay, temporary)
```

---

## 🔒 Security Considerations

### 1. **No External Dependencies**
- Pure JavaScript
- No CDN loads
- No external scripts
- `@grant none`

### 2. **DOM Isolation**
- High z-index (999998, 999999)
- Unique IDs
- Minimal global pollution

### 3. **Sandboxed Execution**
- Runs in IIFE
- Strict mode
- No eval()

---

## 🧪 Testability

### Module Design Benefits

1. **Pure Functions** (utils.js)
   - Easy to unit test
   - Predictable output
   - No side effects

2. **Dependency Injection**
   - Modules import only what they need
   - Easy to mock dependencies
   - Isolated testing

3. **Single Responsibility**
   - Small, focused functions
   - Easy to test edge cases
   - Clear test boundaries

---

## 📚 Future Improvements

### Potential Enhancements

1. **TypeScript Migration**
   - Type safety
   - Better IDE support
   - Catch errors at compile-time

2. **Unit Tests**
   - Jest or Vitest
   - Test coverage reports
   - CI/CD integration

3. **Bundle Optimization**
   - Minification
   - Tree shaking
   - Source maps

4. **Plugin System**
   - Custom handlers
   - Platform extensions
   - User plugins

5. **State Persistence**
   - LocalStorage
   - IndexedDB
   - Export/Import settings

---

## 🎓 Learning Resources

### Understanding the Codebase

**Start Here**:
1. Read `src/main.js` - Entry point
2. Follow `src/interceptors/` - Network layer
3. Trace to `src/handlers/response.js` - Business logic
4. Explore `src/ui/gui.js` - Presentation

**Key Concepts**:
- ES6 Modules
- Closures and IIFEs
- Event delegation
- Debouncing and throttling
- Hash algorithms (FNV-1a)

---

**Architecture designed for maintainability, performance, and extensibility** 🚀

