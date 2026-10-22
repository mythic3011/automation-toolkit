#!/bin/bash
# myCustomScript Complete Project Restructure Script
# This script reorganizes the entire project into a monorepo structure

set -e  # Exit on error

echo "================================================"
echo "myCustomScript Project Restructure"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Auto-navigate to project root if we're in tools/
if [ -f "../README.md" ] && [ ! -f "README.md" ]; then
    print_info "Detected running from tools directory, navigating to project root..."
    cd ..
fi

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    print_error "Cannot find project root. Please ensure you're in the project directory."
    print_error "Expected to find README.md in current directory."
    echo ""
    print_info "Current directory: $(pwd)"
    print_info "Try: cd /path/to/myCustomScript && ./tools/restructure.sh"
    exit 1
fi

# Create backup
print_info "Creating backup branch..."
git checkout -b restructure-backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Create new directory structure (already done)
print_info "Directory structure already created"

# ===================================================================
# PHASE 1: Move media-catcher (already completed)
# ===================================================================
print_info "Phase 1: media-catcher already restructured ✓"

# ===================================================================
# PHASE 2: Restructure fmtools
# ===================================================================
print_info "Phase 2: Restructuring fmtools..."

# Create fmtools subdirectories
mkdir -p packages/fmtools/{src,rust,docs,tests,examples,scripts}

# Move Python source
if [ -d "fmtools" ] && [ ! -d "packages/fmtools/src/fmtools" ]; then
    print_info "Moving Python source code..."
    cp -r fmtools packages/fmtools/src/
fi

# Move Rust source
if [ -d "rust_tools" ] && [ ! -d "packages/fmtools/rust" ]; then
    print_info "Moving Rust implementations..."
    cp -r rust_tools/* packages/fmtools/rust/ 2>/dev/null || true
fi

# Move Python scripts
if [ -d "scripts" ]; then
    print_info "Copying standalone scripts to fmtools..."
    cp scripts/*.py packages/fmtools/scripts/ 2>/dev/null || true
fi

# Move configuration files
for file in pyproject.toml requirements.txt setup.py MANIFEST.in; do
    if [ -f "$file" ]; then
        print_info "Moving $file..."
        cp "$file" packages/fmtools/
    fi
done

# Move installation scripts
for file in install.sh install.bat build_all.sh; do
    if [ -f "$file" ]; then
        print_info "Moving $file..."
        cp "$file" packages/fmtools/
    fi
done

# Move examples
if [ -d "examples" ]; then
    print_info "Moving examples..."
    cp -r examples/* packages/fmtools/examples/ 2>/dev/null || true
fi

# Move build configs
if [ -d "build-config" ]; then
    print_info "Moving build configs..."
    mkdir -p packages/fmtools/build-config
    cp -r build-config/* packages/fmtools/build-config/ 2>/dev/null || true
fi

# Move exe files to packages/fmtools/dist
if [ -d "exe" ]; then
    print_info "Moving executables to dist..."
    mkdir -p packages/fmtools/dist
    cp -r exe/* packages/fmtools/dist/ 2>/dev/null || true
fi

# ===================================================================
# PHASE 3: Restructure linux-automation
# ===================================================================
print_info "Phase 3: Restructuring linux-automation..."

if [ -d "linux" ]; then
    print_info "Moving linux configuration..."
    cp -r linux/* packages/linux-automation/ 2>/dev/null || true
fi

# ===================================================================
# PHASE 4: Restructure scripts
# ===================================================================
print_info "Phase 4: Organizing standalone scripts..."

if [ -d "scripts" ]; then
    mkdir -p packages/scripts/python
    cp scripts/*.py packages/scripts/python/ 2>/dev/null || true
fi

# ===================================================================
# PHASE 5: Organize Documentation
# ===================================================================
print_info "Phase 5: Organizing documentation..."

# Move docs to master docs
if [ -d "docs" ]; then
    # Move fmtools docs
    for doc in INSTALL.md QUICK_START.md USAGE_EXAMPLES.md COMMAND_REFERENCE.md USE_RUST_GUIDE.md; do
        if [ -f "docs/$doc" ]; then
            cp "docs/$doc" packages/fmtools/docs/
        fi
    done
    
    # Keep project-wide docs in docs/master/
    for doc in INDEX.md GETTING_STARTED.md PROJECT_COMPLETE.md WHATS_NEW.md CHANGELOG.md; do
        if [ -f "docs/$doc" ]; then
            cp "docs/$doc" docs/master/
        fi
    done
fi

# Move scattered documentation
for doc in TROUBLESHOOTING.md ZOOM_VTT_SUPPORT.md PERFORMANCE_IMPROVEMENTS.md MODERN_UI_IMPROVEMENTS.md panopto-xhr-catcher-README.md; do
    if [ -f "$doc" ]; then
        cp "$doc" media-catcher/docs/ 2>/dev/null || true
    fi
done

# ===================================================================
# PHASE 6: Create Package READMEs
# ===================================================================
print_info "Phase 6: Creating package READMEs..."

# fmtools README (point to existing)
if [ -f "packages/fmtools/README.md" ]; then
    print_info "fmtools README already exists"
else
    cat > packages/fmtools/README.md << 'EOF'
# fmtools - File Management Tools

> **Professional file management toolkit with unified CLI and ultra-fast Rust implementations**

See the main [README](../../README.md) for complete documentation.

## Quick Start

```bash
# Install
./install.sh

# Use CLI
fmtools --help
```

## Documentation

- [Installation Guide](docs/INSTALL.md)
- [Quick Start](docs/QUICK_START.md)
- [Usage Examples](docs/USAGE_EXAMPLES.md)
- [Command Reference](docs/COMMAND_REFERENCE.md)
- [Rust Guide](docs/USE_RUST_GUIDE.md)
EOF
fi

# linux-automation README
cat > packages/linux-automation/README.md << 'EOF'
# Linux Automation Toolkit

> **Complete Linux server setup and management toolkit**

## What's Inside

- **Nginx** - Complete web server configuration
- **PostgreSQL** - Database setup and management
- **Docker Services** - Containerized applications
- **Scripts** - Automation scripts for common tasks
- **Security** - Hardening and security configurations

## Quick Start

```bash
# Run main setup script
./scripts/setup.sh

# Or use specific scripts
./scripts/nginx/setup-nginx.sh
./scripts/postgresql/setup-postgresql.sh
```

## Documentation

See [docs/](docs/) directory for detailed guides.
EOF

# scripts README
cat > packages/scripts/README.md << 'EOF'
# Utility Scripts Collection

> **Collection of standalone utility scripts**

## Python Scripts

Located in `python/` directory:

- `convert_media.py` - Media file conversion
- `delete_duplicates.py` - Find and remove duplicate files
- `organize_files.py` - Organize files by type/date
- `rename.py` - Batch file renaming
- `file_stats.py` - File statistics
- `clean_empty_dirs.py` - Remove empty directories
- `speed.py` - Speed testing utilities

## Usage

```bash
cd python
python script_name.py --help
```

## Shell Scripts

See `packages/linux-automation/scripts/` for shell scripts.
EOF

print_info "Phase 6 complete ✓"

# ===================================================================
# SUMMARY
# ===================================================================
echo ""
echo "================================================"
echo "Restructure Complete!"
echo "================================================"
echo ""
print_info "New structure created in packages/:"
echo "  - packages/fmtools/          (File management tools)"
echo "  - packages/media-catcher/    (UserScript for media capture)"
echo "  - packages/linux-automation/ (Linux server tools)"
echo "  - packages/scripts/          (Standalone utilities)"
echo ""
print_warn "IMPORTANT: Old files are still in place!"
print_warn "Review the new structure, then manually remove old files."
echo ""
print_info "Next steps:"
echo "  1. Review packages/ directory"
echo "  2. Test each package"
echo "  3. Update import paths if needed"
echo "  4. Remove old files when confident"
echo "  5. Commit changes"
echo ""
echo "================================================"

