#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from src.main import run_debian_setup

if __name__ == "__main__":
    # Safety check to ensure it's run from the venv
    if "VIRTUAL_ENV" not in os.environ:
        print("Error: This script should be launched by install.py.", file=sys.stderr)
        sys.exit(1)
        
    run_debian_setup()