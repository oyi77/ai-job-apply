#!/usr/bin/env python3
"""Check test coverage and identify gaps."""

import subprocess
import sys
from pathlib import Path


def run_coverage_check():
    """Run pytest with coverage and analyze results."""
    print("Running test coverage analysis...")
    print("=" * 60)
    
    # Run pytest with coverage
    result = subprocess.run(
        [
            "pytest",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=json",
            "-v"
        ],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Check coverage percentage
    if "TOTAL" in result.stdout:
        lines = result.stdout.split("\n")
        for line in lines:
            if "TOTAL" in line:
                print("\n" + "=" * 60)
                print("COVERAGE SUMMARY:")
                print(line)
                break
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_coverage_check()
    sys.exit(0 if success else 1)

