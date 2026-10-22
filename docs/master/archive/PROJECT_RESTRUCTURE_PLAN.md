# 🏗️ myCustomScript - Complete Project Restructure Plan

## 📊 Current State Analysis

### Project Components Identified

1. **fmtools** - File Management Tools (Python package with CLI)
2. **rust_tools** - High-performance Rust implementations
3. **scripts** - Standalone Python scripts
4. **linux** - Linux server configuration & automation
5. **media-catcher** - UserScript for media capture (✅ Already restructured)
6. **Documentation** - Scattered across multiple locations
7. **Build artifacts** - exe files, logs, egg-info

### Issues with Current Structure

❌ **Mixed concerns** - Multiple unrelated projects in one repo
❌ **Documentation chaos** - Docs scattered everywhere
❌ **No clear entry point** - Unclear what the project does
❌ **Build artifacts committed** - exe, logs, egg-info shouldn't be in git
❌ **Unclear dependencies** - Hard to understand relationships
❌ **No monorepo structure** - No clear sub-project organization

---

## 🎯 Proposed New Structure

### Option 1: Monorepo with Sub-Projects

```
myCustomScript/
├── README.md                    # Master overview
├── .gitignore                   # Root gitignore
├── LICENSE                      # MIT license
│
├── packages/                    # All sub-projects
│   │
│   ├── fmtools/                # File Management Tools
│   │   ├── src/
│   │   │   └── fmtools/        # Python package
│   │   ├── rust/               # Rust implementations
│   │   ├── docs/               # fmtools documentation
│   │   ├── tests/              # Tests
│   │   ├── examples/           # Example configurations
│   │   ├── pyproject.toml      # Python config
│   │   ├── Cargo.toml          # Rust workspace
│   │   ├── README.md           # fmtools README
│   │   └── install.sh/bat      # Installation scripts
│   │
│   ├── media-catcher/          # UserScript (✅ Done)
│   │   ├── src/                # Modular source
│   │   ├── build/              # Build system
│   │   ├── dist/               # Build output
│   │   ├── docs/               # Documentation
│   │   ├── package.json        # NPM config
│   │   └── README.md           # media-catcher README
│   │
│   ├── linux-automation/       # Linux server tools
│   │   ├── ansible/            # Ansible playbooks
│   │   ├── terraform/          # Infrastructure as code
│   │   ├── kubernetes/         # K8s configs
│   │   ├── scripts/            # Shell scripts
│   │   ├── configs/            # Service configs
│   │   │   ├── nginx/
│   │   │   ├── postgresql/
│   │   │   └── docker/
│   │   ├── docs/               # Documentation
│   │   └── README.md           # Linux automation README
│   │
│   └── scripts/                # Standalone utilities
│       ├── python/             # Python scripts
│       ├── shell/              # Shell scripts
│       ├── docs/               # Script documentation
│       └── README.md           # Scripts README
│
├── docs/                       # Master documentation
│   ├── INDEX.md                # Documentation index
│   ├── GETTING_STARTED.md      # Quick start for all projects
│   ├── CONTRIBUTING.md         # How to contribute
│   ├── ARCHITECTURE.md         # Overall architecture
│   └── PROJECT_GUIDE.md        # Which project to use when
│
├── tools/                      # Development tools
│   ├── build-all.sh            # Build all projects
│   ├── test-all.sh             # Test all projects
│   └── setup-dev.sh            # Setup dev environment
│
└── .github/                    # GitHub workflows
    └── workflows/
        ├── fmtools-ci.yml
        ├── media-catcher-ci.yml
        └── linux-automation-ci.yml
```

### Option 2: Separate Repositories (Recommended for Large Teams)

```
myCustomScript-org/
├── fmtools                     # Separate repo
├── media-catcher               # Separate repo
├── linux-automation            # Separate repo
└── scripts-collection          # Separate repo
```

---

## 📦 Detailed Restructuring Plan

### Phase 1: Preparation & Cleanup

#### 1.1 Create Backup

```bash
# Create backup branch
git checkout -b backup-before-restructure
git push origin backup-before-restructure
```

#### 1.2 Clean Build Artifacts

- Remove from git:
  - `*.exe` files
  - `*.log` files
  - `__pycache__/`
  - `fmtools.egg-info/`
  - `rust_tools/target/`
  - `node_modules/`

#### 1.3 Update .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Rust
target/
Cargo.lock
**/*.rs.bk

# Node
node_modules/
dist/
*.log

# Executables
*.exe

# Logs
logs/
*.log

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Phase 2: Reorganize fmtools

#### 2.1 Create New Structure

```bash
mkdir -p packages/fmtools/{src/fmtools,rust,docs,tests,examples}
```

#### 2.2 Move Files

```bash
# Python source
mv fmtools/ packages/fmtools/src/

# Rust source
mv rust_tools/ packages/fmtools/rust/

# Docs
mv docs/*.md packages/fmtools/docs/

# Examples
mv examples/ packages/fmtools/

# Config files
mv pyproject.toml packages/fmtools/
mv requirements.txt packages/fmtools/
mv setup.py packages/fmtools/
mv MANIFEST.in packages/fmtools/

# Scripts
mv install.sh packages/fmtools/
mv install.bat packages/fmtools/
mv build_all.sh packages/fmtools/
```

#### 2.3 Update Import Paths

Update all Python imports to reflect new structure.

#### 2.4 Update Rust Workspace

```toml
# packages/fmtools/rust/Cargo.toml
[workspace]
members = [
    "convert_media_rs",
    "delete_duplicates_rs",
    "organize_files_rs",
    "rename_files_rs",
]
```

### Phase 3: Reorganize Linux Automation

#### 3.1 Create Structure

```bash
mkdir -p packages/linux-automation/{ansible,terraform,kubernetes,scripts,configs,docs}
```

#### 3.2 Move Files

```bash
# Move linux/ to packages/linux-automation/
mv linux/ packages/linux-automation/src/

# Reorganize inside
cd packages/linux-automation/
# Restructure based on tool type
```

### Phase 4: Organize Standalone Scripts

#### 4.1 Create Structure

```bash
mkdir -p packages/scripts/{python,shell,docs}
```

#### 4.2 Categorize Scripts

```bash
# Move Python scripts
mv scripts/*.py packages/scripts/python/

# Move shell scripts
mv linux/scripts/*.sh packages/scripts/shell/
```

### Phase 5: Master Documentation

#### 5.1 Create docs/

```bash
mkdir -p docs
```

#### 5.2 Create Master README

See detailed README template below.

#### 5.3 Create Documentation Index

```bash
# docs/INDEX.md
- Link to all sub-project docs
- Overview of entire project
- Quick navigation
```

### Phase 6: Development Tools

#### 6.1 Create tools/

```bash
mkdir -p tools
```

#### 6.2 Create Build Scripts

```bash
# tools/build-all.sh
#!/bin/bash
cd packages/fmtools && ./build.sh
cd ../media-catcher && npm run build
# ... etc
```

---

## 📝 New Master README Template

````markdown
# myCustomScript - Professional Automation Toolkit

> **A comprehensive collection of automation tools for file management, media capture, and Linux server administration**

## 🎯 What's Inside

This monorepo contains multiple independent but complementary projects:

### 📁 [fmtools](packages/fmtools/) - File Management Tools

Professional file management toolkit with Python CLI and Rust performance.

- File organization & deduplication
- Media conversion & compression
- Smart file operations
- 10-50x faster with Rust

### 🎬 [media-catcher](packages/media-catcher/) - Media Capture UserScript

Browser UserScript for capturing educational content.

- Panopto JSON capture
- Zoom VTT transcripts
- Modern GUI with auto-download
- Smart deduplication

### 🐧 [linux-automation](packages/linux-automation/) - Server Automation

Complete Linux server setup and management toolkit.

- Nginx configuration
- PostgreSQL setup
- Docker services
- Monitoring & security

### 📜 [scripts](packages/scripts/) - Utility Scripts

Collection of standalone automation scripts.

- Python utilities
- Shell scripts
- Common tasks automation

## 🚀 Quick Start

### Choose Your Project

**File Management?** → [fmtools](packages/fmtools/)
**Media Capture?** → [media-catcher](packages/media-catcher/)
**Linux Setup?** → [linux-automation](packages/linux-automation/)
**Quick Scripts?** → [scripts](packages/scripts/)

### Installation

Each project has its own installation:

```bash
# fmtools
cd packages/fmtools && ./install.sh

# media-catcher
cd packages/media-catcher && npm install && npm run build

# linux-automation
cd packages/linux-automation && ./setup.sh
```
````

## 📚 Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Project Guide](docs/PROJECT_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Contributing](docs/CONTRIBUTING.md)

## 🏗️ Project Structure

```
myCustomScript/
├── packages/          # All sub-projects
│   ├── fmtools/
│   ├── media-catcher/
│   ├── linux-automation/
│   └── scripts/
├── docs/              # Master documentation
├── tools/             # Development tools
└── README.md          # This file
```

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🔗 Links

- [Documentation Index](docs/INDEX.md)
- [Changelog](docs/CHANGELOG.md)
- [FAQ](docs/FAQ.md)

````

---

## 🔄 Migration Steps

### Step-by-Step Execution

1. **Backup Everything**
   ```bash
   git checkout -b restructure
   git add -A
   git commit -m "chore: backup before restructure"
````

2. **Create New Structure**

   ```bash
   mkdir -p packages/{fmtools,media-catcher,linux-automation,scripts}
   mkdir -p docs tools
   ```

3. **Move media-catcher (Already Done)**

   ```bash
   # Already completed!
   ```

4. **Move fmtools**

   ```bash
   # Execute fmtools migration script
   ./tools/migrate-fmtools.sh
   ```

5. **Move linux-automation**

   ```bash
   # Execute linux migration script
   ./tools/migrate-linux.sh
   ```

6. **Move scripts**

   ```bash
   # Execute scripts migration script
   ./tools/migrate-scripts.sh
   ```

7. **Update All Paths**

   - Update import statements
   - Update documentation links
   - Update CI/CD paths

8. **Test Everything**

   ```bash
   ./tools/test-all.sh
   ```

9. **Commit and Push**
   ```bash
   git add -A
   git commit -m "feat: restructure entire project into monorepo"
   git push origin restructure
   ```

---

## ⚠️ Breaking Changes

### For Users

- **Installation paths changed**

  - Old: `python scripts/convert_media.py`
  - New: `cd packages/fmtools && fmtools convert`

- **Documentation moved**
  - Old: `docs/INSTALL.md`
  - New: `packages/fmtools/docs/INSTALL.md`

### Migration Guide for Users

Provide clear migration guide:

```markdown
# Upgrading to v3.0 (Restructured)

## If you're using fmtools

1. Uninstall old version: `pip uninstall fmtools`
2. Install new version: `cd packages/fmtools && ./install.sh`

## If you're using media-catcher

1. Uninstall old UserScript
2. Install new build: `packages/media-catcher/dist/media-catcher.user.js`

## If you're using linux scripts

1. Update your paths
2. New location: `packages/linux-automation/scripts/`
```

---

## 📊 Benefits of Restructure

### ✅ Clarity

- Clear project boundaries
- Each project has own README
- Easy to understand what goes where

### ✅ Maintainability

- Independent versioning
- Separate dependencies
- Isolated changes

### ✅ Scalability

- Easy to add new projects
- Can split into separate repos later
- Clear ownership

### ✅ Developer Experience

- Work on one project at a time
- Clear build/test processes
- Better IDE support

### ✅ CI/CD

- Independent pipelines
- Faster builds (only changed projects)
- Better error isolation

---

## 🎯 Success Criteria

- [ ] All code organized into packages/
- [ ] Each package has own README
- [ ] Master README links to all packages
- [ ] All docs organized
- [ ] All imports updated
- [ ] All tests passing
- [ ] Build scripts work
- [ ] Installation scripts work
- [ ] Documentation is current
- [ ] Git history preserved
- [ ] CI/CD updated

---

## ⏱️ Estimated Timeline

- **Phase 1 (Cleanup)**: 1 hour
- **Phase 2 (fmtools)**: 2-3 hours
- **Phase 3 (Linux)**: 1-2 hours
- **Phase 4 (Scripts)**: 1 hour
- **Phase 5 (Docs)**: 2 hours
- **Phase 6 (Tools)**: 1 hour
- **Testing**: 2 hours

**Total**: ~10-12 hours

---

## 🚧 Risks & Mitigation

### Risk: Breaking existing users

**Mitigation**: Provide clear migration guide, keep old structure in branch

### Risk: Complex git history

**Mitigation**: Use `git mv` to preserve history

### Risk: Import path issues

**Mitigation**: Thorough testing, automated path updates

### Risk: CI/CD breakage

**Mitigation**: Update all workflows before merging

---

## 🎉 Post-Restructure

### Immediate Tasks

1. Update all documentation links
2. Create migration guide for users
3. Tag release as v3.0
4. Announce restructure

### Future Improvements

1. Add monorepo tooling (Turborepo, Lerna)
2. Shared configuration files
3. Cross-project testing
4. Automated releases

---

**This restructure will transform the project from a collection of scripts into a professional, maintainable monorepo!** 🚀
