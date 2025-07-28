#!/usr/bin/env python3
"""
Quick runner for NPPES processing
"""
import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Running NPPES Processing Script...")
    try:
        result = subprocess.run([sys.executable, "scripts/process_nppes_single_year.py"], 
                              capture_output=False, text=True)
        print(f"Script completed with exit code: {result.returncode}")
    except Exception as e:
        print(f"Error running script: {e}") 