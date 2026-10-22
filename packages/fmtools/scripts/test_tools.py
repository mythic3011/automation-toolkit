#!/usr/bin/env python3
"""
Quick test script to verify all tools are working correctly.
This creates a temporary test environment and runs basic tests.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def print_header(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_python_tools():
    """Test Python tools."""
    print_header("Testing Python Tools")
    
    tools = [
        ("delete_duplicates.py", "--help"),
        ("rename.py", "--help"),
        ("speed.py", "--help"),
        ("convert_media.py", "--help"),
        ("organize_files.py", "--help"),
        ("clean_empty_dirs.py", "--help"),
        ("file_stats.py", "--help"),
    ]
    
    passed = 0
    failed = 0
    
    for tool, arg in tools:
        cmd = f"python {tool} {arg}"
        success, stdout, stderr = run_command(cmd)
        
        if success or "usage:" in stdout.lower() or "usage:" in stderr.lower():
            print(f"[PASS] {tool}")
            passed += 1
        else:
            print(f"[FAIL] {tool}")
            failed += 1
    
    return passed, failed

def test_rust_tools():
    """Test Rust executables."""
    print_header("Testing Rust Tools")
    
    tools = [
        "dupeforge-rs.exe",
        "rename_files.exe",
        "organize_files.exe",
        "convert_media.exe",
    ]
    
    passed = 0
    failed = 0
    
    for tool in tools:
        exe_path = os.path.join("exe", tool)
        
        if not os.path.exists(exe_path):
            print(f"[FAIL] {tool} - NOT FOUND")
            failed += 1
            continue
        
        cmd = f"{exe_path} --help"
        success, stdout, stderr = run_command(cmd)
        
        if success or "usage:" in stdout.lower() or "usage:" in stderr.lower():
            print(f"[PASS] {tool}")
            passed += 1
        else:
            print(f"[FAIL] {tool}")
            failed += 1
    
    return passed, failed

def test_documentation():
    """Test that documentation files exist."""
    print_header("Testing Documentation")
    
    docs = [
        "README.md",
        "CHANGELOG.md",
        "QUICK_START.md",
        "USAGE_EXAMPLES.md",
        "IMPLEMENTATION_SUMMARY.md",
        "requirements.txt",
        "example_categories.json",
        ".gitignore",
    ]
    
    passed = 0
    failed = 0
    
    for doc in docs:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            if size > 0:
                print(f"[PASS] {doc:35s} ({size:,} bytes)")
                passed += 1
            else:
                print(f"[FAIL] {doc:35s} - EMPTY")
                failed += 1
        else:
            print(f"[FAIL] {doc:35s} - MISSING")
            failed += 1
    
    return passed, failed

def test_functional():
    """Test basic functionality with temporary files."""
    print_header("Testing Basic Functionality")
    
    passed = 0
    failed = 0
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        test_files = [
            "test1.txt",
            "test2.txt",
            "test3.gif",
            "duplicate.txt",
        ]
        
        for filename in test_files:
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Test content for {filename}\n")
        
        # Create duplicate
        shutil.copy(
            os.path.join(tmpdir, "test1.txt"),
            os.path.join(tmpdir, "test1_copy.txt")
        )
        
        # Test 1: File stats (dry run)
        cmd = f"python file_stats.py --directory \"{tmpdir}\""
        success, stdout, stderr = run_command(cmd)
        if success and "Total files:" in stdout:
            print(f"[PASS] file_stats.py - found files in test directory")
            passed += 1
        else:
            print(f"[FAIL] file_stats.py")
            failed += 1
        
        # Test 2: Delete duplicates (dry run)
        cmd = f"python delete_duplicates.py \"{tmpdir}\" --dry-run"
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"[PASS] delete_duplicates.py - dry-run completed")
            passed += 1
        else:
            print(f"[FAIL] delete_duplicates.py")
            failed += 1
        
        # Test 3: Organize files (dry run)
        cmd = f"python organize_files.py --source \"{tmpdir}\" --mode type --dry-run"
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"[PASS] organize_files.py - dry-run completed")
            passed += 1
        else:
            print(f"[FAIL] organize_files.py")
            failed += 1
    
    return passed, failed

def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("  Automation Toolkit - Verification Tests")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Run all test suites
    p, f = test_python_tools()
    total_passed += p
    total_failed += f
    
    p, f = test_rust_tools()
    total_passed += p
    total_failed += f
    
    p, f = test_documentation()
    total_passed += p
    total_failed += f
    
    p, f = test_functional()
    total_passed += p
    total_failed += f
    
    # Summary
    print_header("Test Summary")
    print(f"Total Passed:  {total_passed}")
    print(f"Total Failed:  {total_failed}")
    print(f"Success Rate:  {(total_passed/(total_passed+total_failed)*100):.1f}%")
    print()
    
    if total_failed == 0:
        print("SUCCESS: All tests passed! Toolkit is ready to use.")
        return 0
    else:
        print(f"WARNING: {total_failed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
