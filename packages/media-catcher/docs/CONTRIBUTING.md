# 🤝 Contributing to Media Catcher

Thank you for your interest in contributing! This guide will help you get started.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Module Guidelines](#module-guidelines)

---

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

---

## 🚀 Getting Started

### Prerequisites

- Node.js >= 14.0.0
- Git
- Text editor (VS Code recommended)
- Tampermonkey browser extension

### Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/media-catcher.git
   cd media-catcher
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build the project**
   ```bash
   npm run build
   ```

4. **Install the UserScript**
   - Open `dist/media-catcher.user.js`
   - Copy contents
   - Open Tampermonkey dashboard
   - Create new script
   - Paste and save

---

## 🔄 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Edit files in `src/` directory:

```
src/
├── core/       # Configuration and utilities
├── data/       # Data processing
├── handlers/   # Business logic
├── interceptors/ # Network layer
└── ui/         # User interface
```

### 3. Build and Test

```bash
# Build
npm run build

# Watch mode (auto-rebuild on changes)
npm run watch

# Lint
npm run lint

# Format
npm run format
```

### 4. Test in Browser

1. Reinstall updated script in Tampermonkey
2. Visit test URLs (Panopto/Zoom)
3. Check console for errors
4. Verify GUI works
5. Test all features

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug"
```

**Commit Message Format**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `perf:` - Performance improvement
- `test:` - Tests
- `chore:` - Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 📏 Code Standards

### JavaScript Style

We use **ESLint** and **Prettier** for consistency.

**Rules**:
- Use ES6 modules (`import`/`export`)
- Use `const` and `let`, not `var`
- Use arrow functions where appropriate
- Use template literals for strings
- Add JSDoc comments for functions
- Keep functions small and focused

**Example**:
```javascript
/**
 * Generate hash using FNV-1a algorithm
 * @param {Object|String} data - Data to hash
 * @returns {String} Hash in base-36
 */
export function generateHash(data) {
  const str = JSON.stringify(data);
  let hash = 2166136261;
  
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash += (hash << 1) + (hash << 4);
  }
  
  return (hash >>> 0).toString(36);
}
```

### Module Organization

**Good**:
```javascript
// ✅ Single responsibility
export function downloadJSON(data, filename) {
  // Only handles JSON download
}

export function downloadVTT(data, filename) {
  // Only handles VTT download
}
```

**Bad**:
```javascript
// ❌ Multiple responsibilities
export function downloadFile(data, filename, type, options) {
  // Does too many things
}
```

### Imports

**Good**:
```javascript
// ✅ Named imports, clear dependencies
import { CONFIG } from "../core/config.js";
import { state } from "../core/state.js";
import { generateHash } from "../core/utils.js";
```

**Bad**:
```javascript
// ❌ Wildcard import, unclear what's used
import * as utils from "../core/utils.js";
```

---

## 🧪 Testing

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Script builds without errors
- [ ] No console errors in browser
- [ ] GUI appears and is draggable
- [ ] All toggles work
- [ ] Requests are captured
- [ ] Download works (JSON and VTT)
- [ ] View in console works
- [ ] Clear all works
- [ ] Notifications appear
- [ ] Deduplication works
- [ ] Size filtering works
- [ ] Data cleaning works (when enabled)

### Testing on Different Platforms

**Panopto**:
- Visit video page
- Play video
- Check for POST to `DeliveryInfo.aspx`
- Verify JSON capture

**Zoom**:
- Visit recording page
- Check for GET to `/rec/play/vtt`
- Verify VTT capture

### Browser Testing

Test on:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if possible)

---

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure your PR**:
   - Has a clear title
   - Describes what changed and why
   - References any related issues
   - Includes screenshots (if UI changes)

2. **PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Tested on Panopto
- [ ] Tested on Zoom
- [ ] Tested on Chrome
- [ ] Tested on Firefox

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Ran `npm run lint`
- [ ] Ran `npm run format`
- [ ] Build succeeds (`npm run build`)
- [ ] Tested in browser
```

3. **Review Process**:
   - Wait for maintainer review
   - Address feedback
   - Make requested changes
   - Update PR

---

## 📦 Module Guidelines

### Adding a New Module

1. **Choose correct directory**:
   - `core/` - Utilities, config, state
   - `data/` - Data processing
   - `handlers/` - Business logic
   - `interceptors/` - Network layer
   - `ui/` - User interface

2. **Create file with exports**:
```javascript
/**
 * Module description
 */

import { dependency } from "./other-module.js";

/**
 * Function description
 */
export function myFunction() {
  // Implementation
}
```

3. **Import in appropriate files**:
```javascript
import { myFunction } from "../path/to/module.js";
```

4. **Update build** (automatic):
   - Build script auto-detects new modules
   - No manual configuration needed

### Modifying Existing Modules

1. **Understand the module's role** (see [ARCHITECTURE.md](ARCHITECTURE.md))
2. **Keep changes focused**
3. **Don't break existing exports**
4. **Update JSDoc comments**
5. **Test thoroughly**

---

## 🎨 UI Contributions

### Adding UI Components

1. **Add to `src/ui/` directory**
2. **Follow existing patterns**:
```javascript
export function showMyComponent(message) {
  const element = document.createElement("div");
  element.style.cssText = `...`;
  element.innerHTML = `...`;
  document.body.appendChild(element);
  // ... cleanup logic
}
```

3. **Add styles to `src/ui/styles.js`**
4. **Use consistent styling**:
   - Purple gradient: `#667eea` → `#764ba2`
   - Rounded corners: `8px` - `12px`
   - Shadows: `0 4px 15px rgba(0,0,0,0.3)`

### Modifying GUI

GUI is in `src/ui/gui.js`. Be careful with:
- Event listeners
- DOM caching (`DOM` object)
- Public API (`window.panoptoCatcher`)

---

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try latest version
3. Test in clean browser profile
4. Check console for errors

### Creating Issue

Include:
- Browser and version
- Tampermonkey version
- UserScript version
- Steps to reproduce
- Expected vs actual behavior
- Console errors
- Screenshots

**Template**:
```markdown
**Environment**
- Browser: Chrome 120
- Tampermonkey: 4.19
- Script Version: 2.4

**Steps to Reproduce**
1. Go to ...
2. Click on ...
3. See error

**Expected Behavior**
Should do X

**Actual Behavior**
Does Y instead

**Console Errors**
```
[Error logs here]
```

**Screenshots**
[If applicable]
```

---

## 💡 Feature Requests

We welcome ideas! Please:

1. **Check existing issues** first
2. **Describe the feature** clearly
3. **Explain the use case**
4. **Consider implementation** (optional)

**Template**:
```markdown
**Feature Description**
Brief description

**Use Case**
Why is this needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches?

**Additional Context**
Screenshots, examples, etc.
```

---

## 🏆 Recognition

Contributors will be:
- Listed in README
- Credited in release notes
- Thanked in commit messages

---

## 📚 Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [MDN Web Docs](https://developer.mozilla.org/)
- [ES6 Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Tampermonkey Documentation](https://www.tampermonkey.net/documentation.php)

---

## 📞 Questions?

- Open an issue with "Question" label
- Check existing documentation
- Look at code examples in `src/`

---

**Thank you for contributing! 🎉**

Every contribution, no matter how small, makes this project better.

