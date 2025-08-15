#!/usr/bin/env python3
"""
Convenience script to run Compliance Assistant without installation.
This script can be used to run the tool directly from the source directory.
"""

import sys
import os

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import and run the CLI
from compliance_assistant.cli import main

if __name__ == "__main__":
    main()
