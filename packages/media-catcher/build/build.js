/**
 * Build script to bundle all modules into a single UserScript file
 * Supports minification and multiple build modes
 */

const fs = require("fs");
const path = require("path");
const { minify } = require("terser");

// Configuration
const SRC_DIR = path.join(__dirname, "../src");
const DIST_DIR = path.join(__dirname, "../dist");
const ENTRY_POINT = path.join(SRC_DIR, "main.js");

// Build mode (development or production)
const BUILD_MODE = process.env.BUILD_MODE || "production";
if (BUILD_MODE !== "production" && BUILD_MODE !== "development") {
  throw new Error("BUILD_MODE must be production or development");
}
const IS_PRODUCTION = BUILD_MODE === "production";

// Output files
const OUTPUT_FILE = path.join(
  DIST_DIR,
  IS_PRODUCTION ? "media-catcher.user.js" : "media-catcher.dev.user.js"
);
const OUTPUT_FILE_MIN = path.join(DIST_DIR, "media-catcher.min.user.js");

// UserScript metadata
const getMetadata = (isMinified = false) => {
  const suffix = isMinified ? " (Minified)" : IS_PRODUCTION ? "" : " (Dev)";
  return `// ==UserScript==
// @name         Media Catcher (Panopto & Zoom)${suffix}
// @namespace    http://tampermonkey.net/
// @version      2.4.${IS_PRODUCTION ? "0" : "0-dev"}
// @description  Catch and save Panopto JSON & Zoom VTT transcripts with GUI - Modular Build
// @author       Automation Toolkit contributors
// @match        https://polyu.ap.panopto.com/*
// @match        https://*.panopto.com/*
// @match        http://polyu.ap.panopto.com/*
// @match        http://*.panopto.com/*
// @match        https://polyu.zoom.us/*
// @match        https://*.zoom.us/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

`;
};

/**
 * Simple module bundler
 */
class ModuleBundler {
  constructor() {
    this.modules = new Map();
    this.processed = new Set();
  }

  /**
   * Read and parse a module file
   */
  readModule(filePath) {
    const content = fs.readFileSync(filePath, "utf8");
    const imports = [];
    const exports = [];

    // Extract imports
    const importRegex = /import\s+{([^}]+)}\s+from\s+["']([^"']+)["'];?/g;
    let match;
    while ((match = importRegex.exec(content)) !== null) {
      const importedNames = match[1].split(",").map((name) => name.trim());
      const importPath = match[2];
      imports.push({ names: importedNames, path: importPath });
    }

    // Extract exports
    const exportRegex = /export\s+(const|function|class)\s+([a-zA-Z0-9_]+)/g;
    while ((match = exportRegex.exec(content)) !== null) {
      exports.push(match[2]);
    }

    return { content, imports, exports };
  }

  /**
   * Resolve relative import path
   */
  resolveImportPath(fromFile, importPath) {
    const fromDir = path.dirname(fromFile);
    const resolved = path.resolve(fromDir, importPath);
    // Add .js extension if not present
    return resolved.endsWith(".js") ? resolved : `${resolved}.js`;
  }

  /**
   * Process a module and its dependencies
   */
  processModule(filePath) {
    if (this.processed.has(filePath)) {
      return;
    }

    // Mark as processed FIRST to prevent circular dependencies
    this.processed.add(filePath);

    const module = this.readModule(filePath);

    // Process dependencies first (recursively)
    for (const importInfo of module.imports) {
      const depPath = this.resolveImportPath(filePath, importInfo.path);
      this.processModule(depPath);
    }

    // Add to modules Map AFTER dependencies are processed
    // This ensures dependencies appear first in the Map
    this.modules.set(filePath, module);
  }

  /**
   * Remove import/export statements and wrap in IIFE
   */
  transformModuleContent(content) {
    // Remove import statements
    content = content.replace(
      /import\s+{[^}]+}\s+from\s+["'][^"']+["'];?\n?/g,
      ""
    );

    // Replace 'export const' with 'const'
    content = content.replace(/export\s+const\s+/g, "const ");

    // Replace 'export function' with 'function'
    content = content.replace(/export\s+function\s+/g, "function ");

    // Replace 'export class' with 'class'
    content = content.replace(/export\s+class\s+/g, "class ");

    return content;
  }

  /**
   * Generate bundle content
   */
  generateBundle() {
    // Build the final bundle
    let bundle = "(function () {\n";
    bundle += `  "use strict";\n\n`;

    // Add all module contents in the order they were processed (dependencies first)
    // Do NOT re-sort, as the processing order already respects dependencies
    const modulesInOrder = Array.from(this.modules.entries());

    for (const [filePath, module] of modulesInOrder) {
      const relativePath = path.relative(SRC_DIR, filePath);
      if (!IS_PRODUCTION) {
        bundle += `  // ==================== Module: ${relativePath} ====================\n`;
      }
      bundle += this.transformModuleContent(module.content);
      bundle += "\n\n";
    }

    bundle += "})();\n";
    return bundle;
  }

  /**
   * Minify the bundle
   */
  async minifyBundle(code) {
    console.log("🗜️  Minifying bundle...");

    try {
      const result = await minify(code, {
        compress: {
          dead_code: true,
          drop_console: false, // Keep console for debugging in production
          drop_debugger: true,
          keep_classnames: true,
          keep_fnames: false,
          passes: 1, // Reduce passes to prevent aggressive reordering
          hoist_vars: false, // Prevent variable hoisting issues
          hoist_funs: false, // Prevent function hoisting issues
          toplevel: false, // Don't hoist to top level
          sequences: false, // Don't join consecutive statements
        },
        mangle: {
          keep_classnames: true,
          keep_fnames: false,
          toplevel: false, // Don't mangle top-level names
        },
        format: {
          comments: false,
          beautify: false,
        },
      });

      if (result.error) {
        console.warn(
          "⚠️  Minification reported an error:",
          result.error.message
        );
        console.log("📝 Falling back to non-minified version");
        return code;
      }
      if (typeof result.code !== "string" || result.code.length === 0) {
        console.warn(
          "⚠️  Minification returned empty code — falling back to non-minified version"
        );
        return code;
      }
      return result.code;
    } catch (error) {
      console.error("⚠️  Minification failed:", error.message);
      console.log("📝 Falling back to non-minified version");
      return code;
    }
  }

  /**
   * Format file size with appropriate units
   */
  formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  /**
   * Calculate compression ratio
   */
  getCompressionRatio(originalSize, minifiedSize) {
    const ratio = ((1 - minifiedSize / originalSize) * 100).toFixed(1);
    return `${ratio}%`;
  }

  /**
   * Build the bundle
   */
  async build() {
    console.log("═══════════════════════════════════════");
    console.log("🔨 Building Media Catcher UserScript");
    console.log("═══════════════════════════════════════");
    console.log(`📂 Entry point: ${ENTRY_POINT}`);
    console.log(`🏗️  Build mode: ${BUILD_MODE.toUpperCase()}`);
    console.log("");

    // Process all modules starting from entry point
    this.processModule(ENTRY_POINT);
    console.log(`✅ Processed ${this.processed.size} modules`);

    // Ensure dist directory exists
    if (!fs.existsSync(DIST_DIR)) {
      fs.mkdirSync(DIST_DIR, { recursive: true });
    }

    // Generate bundle
    const bundleCode = this.generateBundle();
    const bundleWithMetadata = getMetadata(false) + bundleCode;

    // Write regular bundle
    fs.writeFileSync(OUTPUT_FILE, bundleWithMetadata, "utf8");
    const regularStats = fs.statSync(OUTPUT_FILE);

    console.log("");
    console.log("📦 Regular Build:");
    console.log(`   File: ${path.basename(OUTPUT_FILE)}`);
    console.log(`   Size: ${this.formatSize(regularStats.size)}`);

    // Create minified version if in production mode
    if (IS_PRODUCTION) {
      console.log("");
      const minifiedCode = await this.minifyBundle(bundleCode);
      // Add ESLint disable comment for minified file to prevent IDE warnings
      const minifiedWithMetadata =
        getMetadata(true) + "/* eslint-disable */\n" + minifiedCode;

      fs.writeFileSync(OUTPUT_FILE_MIN, minifiedWithMetadata, "utf8");
      const minifiedStats = fs.statSync(OUTPUT_FILE_MIN);

      console.log("📦 Minified Build:");
      console.log(`   File: ${path.basename(OUTPUT_FILE_MIN)}`);
      console.log(`   Size: ${this.formatSize(minifiedStats.size)}`);
      console.log(
        `   Saved: ${this.formatSize(regularStats.size - minifiedStats.size)} (${this.getCompressionRatio(regularStats.size, minifiedStats.size)})`
      );
    }

    console.log("");
    console.log("═══════════════════════════════════════");
    console.log("✅ Build complete!");
    console.log("🎉 Ready to install in Tampermonkey!");
    console.log("═══════════════════════════════════════");
  }
}

// Run the build
(async () => {
  try {
    const bundler = new ModuleBundler();
    await bundler.build();
  } catch (error) {
    console.error("❌ Build failed:", error);
    console.error(error.stack);
    process.exit(1);
  }
})();
