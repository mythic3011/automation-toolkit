# Build System Documentation

## Overview

The media-catcher project uses a custom build system with support for:

- **Module bundling** - Combines 14+ ES6 modules into a single UserScript
- **Minification** - Uses Terser to reduce file size by ~33%
- **Multiple build modes** - Development and Production configurations
- **Cross-platform** - Works on Windows, macOS, and Linux

---

## Build Modes

### Production Mode (Default)

- **Minifies** the output using Terser
- **Removes** module comments and dead code
- **Generates** two files:
  - `media-catcher.user.js` (regular, ~40 KB)
  - `media-catcher.min.user.js` (minified, ~26 KB)
- **Optimizes** for smaller file size

### Development Mode

- **No minification** for easier debugging
- **Includes** module comments showing file structure
- **Generates** one file:
  - `media-catcher.dev.user.js` (~41 KB)
- **Optimizes** for readability

---

## Build Commands

### Quick Reference

```bash
# Production build (default) - creates minified version
npm run build

# Production build (explicit)
npm run build:prod

# Development build - no minification
npm run build:dev
npm run dev

# Watch mode - rebuilds on file changes (development)
npm run watch

# Clean dist directory
npm run clean
```

### Detailed Commands

#### `npm run build`

Default production build with minification.

```bash
npm run build
```

**Output:**

- `dist/media-catcher.user.js` (39.89 KB)
- `dist/media-catcher.min.user.js` (26.48 KB)

**Use when:** Creating a release or final version for production use.

---

#### `npm run build:dev`

Development build without minification.

```bash
npm run build:dev
```

**Output:**

- `dist/media-catcher.dev.user.js` (40.88 KB)

**Use when:** Developing and debugging. Easier to read, includes module comments.

---

#### `npm run dev`

Shortcut for development build with a completion message.

```bash
npm run dev
```

---

#### `npm run watch`

Automatically rebuilds when source files change.

```bash
npm run watch
```

**Use when:** Actively developing. Monitors `src/` directory for changes.

---

#### `npm run clean`

Removes all files from the `dist/` directory.

```bash
npm run clean
```

**Note:** This runs automatically before `build` and `build:prod`.

---

## Build Output

### File Comparison

| File                        | Mode        | Size   | Minified | Use Case                 |
| --------------------------- | ----------- | ------ | -------- | ------------------------ |
| `media-catcher.user.js`     | Production  | ~40 KB | No       | Standard production use  |
| `media-catcher.min.user.js` | Production  | ~26 KB | Yes      | Optimized production use |
| `media-catcher.dev.user.js` | Development | ~41 KB | No       | Development & debugging  |

### Size Comparison

```
Regular:   39.89 KB (100%)
Minified:  26.48 KB (66.4%)
Saved:     13.42 KB (33.6%)
```

**Recommendation:** Use the minified version for production to save bandwidth and improve load times.

---

## Build Process

### Steps

1. **Clean** - Remove old build artifacts (automatic)
2. **Parse** - Read and analyze all 14 source modules
3. **Bundle** - Combine modules into single file
4. **Transform** - Remove import/export syntax
5. **Minify** - Compress code (production only)
6. **Write** - Save output file(s)

### Module Processing Order

Modules are bundled in dependency order:

```
1. Core modules (config, state, utils)
2. Data modules (cleaner, downloader, deduplication)
3. Handler modules (response)
4. UI modules (styles, notifications, dialogs, gui)
5. Interceptor modules (xhr, fetch)
6. Main entry point
```

---

## Minification Options

The build system uses **Terser** with the following configuration:

### Compression Options

```javascript
compress: {
  dead_code: true,        // Remove unreachable code
  drop_console: false,    // Keep console.log for debugging
  drop_debugger: true,    // Remove debugger statements
  keep_classnames: true,  // Preserve class names
  keep_fnames: false,     // Minify function names
  passes: 2,              // Two compression passes
}
```

### Mangling Options

```javascript
mangle: {
  keep_classnames: true,  // Preserve class names
  keep_fnames: false,     // Minify function names
}
```

### Format Options

```javascript
format: {
  comments: false,        // Remove all comments
  beautify: false,        // Minify output
}
```

**Why keep console logs?** Useful for production debugging without compromising much on size.

---

## Development Workflow

### Recommended Setup

1. **Initial Setup**

   ```bash
   npm install
   ```

2. **Start Development**

   ```bash
   npm run watch
   ```

   This will rebuild automatically when you save files.

3. **Test Changes**
   - Open Tampermonkey
   - Install `dist/media-catcher.dev.user.js`
   - Refresh the page to test

4. **Lint & Format**

   ```bash
   npm run lint
   npm run format
   ```

5. **Production Build**
   ```bash
   npm run build
   ```
   Install `dist/media-catcher.min.user.js` for final testing.

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build UserScript

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: |
          cd packages/media-catcher
          npm install

      - name: Lint
        run: |
          cd packages/media-catcher
          npm run lint

      - name: Build
        run: |
          cd packages/media-catcher
          npm run build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: userscript
          path: packages/media-catcher/dist/*.user.js
```

---

## Troubleshooting

### Build Fails

**Problem:** Build command fails with error

```bash
npm run build
# Error: Cannot find module 'terser'
```

**Solution:** Install dependencies

```bash
npm install
```

---

### Minification Fails

**Problem:** Minification fails but build continues

```
⚠️  Minification failed: ...
📝 Falling back to non-minified version
```

**Solution:** This is expected behavior. The build will complete with a non-minified file. Check the error message for details.

---

### Watch Mode Not Working

**Problem:** Changes aren't triggering rebuilds

```bash
npm run watch
# Files change but no rebuild
```

**Solution:** Ensure you're editing files in `src/` directory. Check nodemon output for errors.

---

### Large File Size

**Problem:** Output file is larger than expected

**Solutions:**

1. Use minified version:

   ```bash
   npm run build
   # Use media-catcher.min.user.js
   ```

2. Check for unnecessary console.log statements

3. Remove unused imports

---

## Performance Considerations

### Build Speed

- **Development build:** ~1-2 seconds
- **Production build (with minification):** ~2-3 seconds

### Output Size

| Metric               | Value             |
| -------------------- | ----------------- |
| Source files         | 14 modules        |
| Total source size    | ~30 KB            |
| Bundled (unminified) | ~40 KB (+33%)     |
| Bundled (minified)   | ~26 KB (-13%)     |
| Gzip compressed      | ~8 KB (estimated) |

**Why is bundled larger?** IIFE wrapper, metadata header, and ESM to browser JS transformation add overhead.

**Optimization tip:** The minified version is actually smaller than the total source size despite bundling!

---

## Future Enhancements

Potential improvements to the build system:

- [ ] Source maps for debugging minified code
- [ ] Tree shaking for unused exports
- [ ] Code splitting for lazy loading
- [ ] Brotli compression statistics
- [ ] Build time analytics
- [ ] Bundle visualization
- [ ] Automatic versioning from git tags

---

## Dependencies

### Build Dependencies

```json
{
  "terser": "^5.31.0", // JavaScript minifier
  "cross-env": "^7.0.3", // Cross-platform environment vars
  "nodemon": "^3.0.1", // File watching for development
  "eslint": "^8.50.0", // Code linting
  "prettier": "^3.0.3" // Code formatting
}
```

### Why These Tools?

- **Terser:** Industry-standard JS minifier, best compression
- **cross-env:** Ensures build scripts work on Windows, Mac, Linux
- **nodemon:** Reliable file watcher with minimal configuration
- **ESLint:** Catches errors before runtime
- **Prettier:** Consistent code style

---

## Advanced Usage

### Custom Build Mode

Create custom build configurations by setting environment variables:

```bash
# Custom mode
BUILD_MODE=custom node build/build.js

# Debug mode (could be implemented)
BUILD_MODE=debug node build/build.js
```

### Programmatic API

Use the bundler in your own scripts:

```javascript
const { ModuleBundler } = require("./build/build.js");

const bundler = new ModuleBundler();
await bundler.build();
```

---

## Best Practices

### For Development

1. Use `npm run watch` during active development
2. Use the dev build for testing (includes module comments)
3. Run `npm run lint` before committing
4. Format code with `npm run format`

### For Production

1. Always build with `npm run build` before release
2. Test both regular and minified versions
3. Use the minified version for distribution
4. Update version number in package.json
5. Tag releases in git

### For CI/CD

1. Run linting before building
2. Build both dev and prod versions
3. Save artifacts for download
4. Test minified version in browser
5. Automated version bumping

---

**Last Updated:** October 2025
**Build System Version:** 2.0
