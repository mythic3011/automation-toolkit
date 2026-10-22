# Automation Toolkit Rename and History Reset Implementation Plan

> Historical plan: the rename and history reset are complete. Media Catcher was removed afterward; its references below describe the earlier snapshot, not the current packages.

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the repository to `mythic3011/automation-toolkit` and replace its Git history with one initial commit containing the current refined files.

**Architecture:** Preserve the current working tree, package names, and prior refinements. Update active branding and links, retain historical documentation and author credits, and publish a parentless snapshot with an explicit lease on the existing remote branch. Store recovery data outside the repository and clear old local refs and reflogs after verifying the published snapshot.

**Tech Stack:** Git, GitHub CLI, Python package metadata, Node.js userscript build tooling.

---

### Task 1: Inspect and preserve the current state

1. Confirm GitHub administrator access, repository identity, and availability of the requested name.
2. Inspect local and remote branches, tags, releases, protections, and worktrees.
3. Save and verify a private Git bundle and a copy of Git metadata outside the checkout.
4. Record both branch tips; preserve current source files in the new snapshot.

### Task 2: Update active branding and repository links

**Files:**
- `README.md` and active guides under `docs/`
- `packages/fmtools/pyproject.toml`
- `packages/media-catcher/package.json`
- `packages/media-catcher/src/core/config.js`
- `packages/media-catcher/build/build.js`
- Legacy helper banners in both script collections

1. Use `Automation Toolkit` for visible branding and `automation-toolkit` for repository paths.
2. Point clone instructions and package metadata to the confirmed owner and repository.
3. Keep package identities, historical archive text, and original author attribution.
4. Check for stale active links, parse metadata, run Media Catcher tests/lint/builds, and rebuild/check the Python distributions.

### Task 3: Publish the renamed repository with fresh history

1. Stage the current refined source, verify whitespace, and inspect the complete snapshot for generated artifacts and unexpected private files.
2. Save and verify a source archive outside the checkout.
3. Create one parentless commit from the verified index tree without checking out or deleting working files.
4. Rename the GitHub repository and update the existing local remote URL.
5. Publish the new commit with `--force-with-lease` pinned to the previously inspected remote tip.
6. Verify repository identity, the remote branch, the one-commit history, and the local working tree.
7. Clear obsolete local refs/reflogs and prune unreachable old Git objects; retain the external recovery backup.

### Verification

- Confirm the GitHub repository ID is unchanged and its name is `mythic3011/automation-toolkit`.
- Confirm GitHub and the local checkout reference the same parentless initial commit.
- Confirm there are no extra branch or tag references keeping old history active.
- Confirm `git rev-list --count --all` returns `1` and the working tree is clean.
- Confirm all previously refined source files, tests, and build sources are included and the removed Linux package is absent.
