# 🏗️ Project Restructure Guide

## ⚠️ Important Notice

This project is being restructured from a flat structure into an organized monorepo. This document guides you through the process.

---

## 🎯 What's Happening?

We're reorganizing `myCustomScript` from this:
```
myCustomScript/
├── fmtools/           # Mixed with other stuff
├── scripts/           # Scattered everywhere
├── linux/             # No clear organization
├── docs/              # Documentation chaos
└── ... 100+ files
```

To this:
```
myCustomScript/
├── packages/          # All sub-projects organized
│   ├── fmtools/
│   ├── media-catcher/
│   ├── linux-automation/
│   └── scripts/
├── docs/              # Master documentation
└── tools/             # Development tools
```

---

## 🚀 Quick Start

### Automated Restructure (Recommended)

**Windows:**
```batch
cd tools
restructure.bat
```

**Linux/Mac:**
```bash
cd tools
chmod +x restructure.sh
./restructure.sh
```

### What the Script Does

✅ **Safe**: Copies files (doesn't delete originals)
✅ **Smart**: Organizes by project type
✅ **Fast**: Completes in seconds
✅ **Reversible**: Old files remain until you're confident

---

## 📋 Manual Steps (If Needed)

If you prefer manual control:

### 1. Create Structure
```bash
mkdir -p packages/{fmtools,media-catcher,linux-automation,scripts}
mkdir -p docs/master tools
```

### 2. Move fmtools
```bash
# Python source
cp -r fmtools packages/fmtools/src/

# Rust source
cp -r rust_tools packages/fmtools/rust/

# Config files
cp pyproject.toml requirements.txt packages/fmtools/

# Scripts
cp install.sh install.bat packages/fmtools/

# Examples
cp -r examples packages/fmtools/

# Executables
cp -r exe packages/fmtools/dist/
```

### 3. Move media-catcher
```bash
# Already done! ✓
```

### 4. Move Linux files
```bash
cp -r linux/* packages/linux-automation/
```

### 5. Move Scripts
```bash
cp scripts/*.py packages/scripts/python/
```

### 6. Organize Documentation
```bash
# fmtools docs
cp docs/INSTALL.md packages/fmtools/docs/
cp docs/QUICK_START.md packages/fmtools/docs/
# ... etc

# Master docs
cp docs/INDEX.md docs/master/
cp docs/GETTING_STARTED.md docs/master/
```

---

## ✅ Verification Checklist

After restructure, verify:

- [ ] `packages/fmtools/` has Python and Rust code
- [ ] `packages/media-catcher/` is complete
- [ ] `packages/linux-automation/` has all Linux files
- [ ] `packages/scripts/` has Python scripts
- [ ] Each package has its own README
- [ ] Documentation is organized
- [ ] Old files still exist (for safety)

---

## 🧪 Testing

### Test fmtools
```bash
cd packages/fmtools
./install.sh
fmtools --help
```

### Test media-catcher
```bash
cd packages/media-catcher
npm install
npm run build
# Install dist/media-catcher.user.js in Tampermonkey
```

### Test Linux scripts
```bash
cd packages/linux-automation/scripts
./setup.sh --help
```

---

## 🗑️ Cleanup (After Testing)

When you're confident everything works:

### 1. Remove Old Files
```bash
# Remove old Python source
rm -rf fmtools/

# Remove old Rust source
rm -rf rust_tools/

# Remove old scripts
rm -rf scripts/

# Remove old Linux files
rm -rf linux/

# Remove old docs
rm -rf docs/*.md

# Remove old executables
rm -rf exe/

# Remove old logs
rm -rf logs/
```

### 2. Update .gitignore
Already updated! See `.gitignore` in root.

### 3. Commit Changes
```bash
git add -A
git commit -m "feat: restructure project into monorepo"
git push
```

---

## 📚 New Documentation Structure

After restructure:

### Master Docs (`docs/master/`)
- Project overview
- Getting started guide
- Architecture
- Contributing guide

### Package Docs
- `packages/fmtools/docs/` - fmtools documentation
- `packages/media-catcher/docs/` - UserScript docs
- `packages/linux-automation/docs/` - Linux setup guides
- `packages/scripts/` - Script usage

---

## 🔄 For Existing Users

### If you're using fmtools

**Before (old)**:
```bash
python scripts/convert_media.py input.mp4 output.webm
```

**After (new)**:
```bash
cd packages/fmtools
fmtools convert input.mp4 output.webm
```

### If you're using media-catcher

**Before (old)**:
```bash
# Install panopto-xhr-catcher.user.js
```

**After (new)**:
```bash
# Install packages/media-catcher/dist/media-catcher.user.js
```

### If you're using Linux scripts

**Before (old)**:
```bash
./linux/scripts/setup.sh
```

**After (new)**:
```bash
./packages/linux-automation/scripts/setup.sh
```

---

## ❓ FAQ

### Why restructure?

- **Clarity**: Each project has clear boundaries
- **Maintainability**: Easier to find and update code
- **Scalability**: Easy to add new projects
- **Professional**: Industry-standard monorepo structure

### Will this break my existing setup?

No! Old files remain until you delete them. The new structure is additive.

### Can I contribute during restructure?

Yes! Contribute to `packages/` directories. Avoid modifying old structure.

### How long does restructure take?

- **Automated**: < 1 minute
- **Manual**: ~30 minutes
- **Testing**: 1-2 hours
- **Cleanup**: 15 minutes

### What if something goes wrong?

1. Old files are still there
2. Git history is preserved
3. You can revert: `git checkout old-branch`
4. Ask for help in issues

---

## 🎉 Benefits

### For Developers
- ✅ Clear project boundaries
- ✅ Independent development
- ✅ Better IDE support
- ✅ Easier testing

### For Users
- ✅ Clear documentation
- ✅ Easy to find what you need
- ✅ Better installation experience
- ✅ Consistent structure

### For Contributors
- ✅ Know where to add features
- ✅ Clear ownership
- ✅ Easy to review changes
- ✅ Better CI/CD

---

## 📞 Support

Having issues? 

1. Check [PROJECT_RESTRUCTURE_PLAN.md](PROJECT_RESTRUCTURE_PLAN.md)
2. Review [TROUBLESHOOTING.md](docs/master/TROUBLESHOOTING.md)
3. Open an issue on GitHub
4. Ask in discussions

---

## 📜 Timeline

- **Phase 1**: Preparation ✅ Complete
- **Phase 2**: Automated scripts ✅ Complete
- **Phase 3**: Documentation ✅ Complete
- **Phase 4**: Testing (You are here)
- **Phase 5**: Cleanup
- **Phase 6**: Release v3.0

---

**Let's make this project amazing! 🚀**

For detailed technical information, see [PROJECT_RESTRUCTURE_PLAN.md](PROJECT_RESTRUCTURE_PLAN.md).

