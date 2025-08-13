#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging
import shutil
import venv

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, ".venv")
LOG_FILE = "setup.log"
RUN_SCRIPT = os.path.join(PROJECT_ROOT, "run.py")

def setup_logging():
    """Sets up logging to a file, clearing the old log on a fresh run."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, mode='w')],
        force=True
    )

def run_bootstrap_command(command, message):
    """Runs a command during bootstrap, showing a simple status and logging all output."""
    logging.info(f"Executing bootstrap command: {' '.join(command)}")
    sys.stdout.write(message)
    sys.stdout.flush()

    try:
        with open(LOG_FILE, 'a') as log_file:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=log_file,
                cwd=PROJECT_ROOT
            )
        process.wait()

        if process.returncode == 0:
            print(" ✅")
            return True
        else:
            print(" ❌")
            logging.error(f"Bootstrap command FAILED. See setup.log for details.")
            sys.exit(1)

    except Exception as e:
        print(" ❌")
        logging.error(f"An unexpected error occurred during bootstrap: {e}")
        sys.exit(1)

# --- Bootstrapping Logic ---
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Root privileges are required. Attempting to re-run with sudo...")
        try:
            os.execv(shutil.which('sudo'), [shutil.which('sudo'), '-E', sys.executable] + sys.argv)
        except Exception as e:
            print(f"❌ Failed to elevate privileges: {e}")
            sys.exit(1)

    setup_logging()
    print("--- Starting Bootstrap Process ---")
    
    # Create or recreate a clean virtual environment
    if os.path.exists(VENV_DIR):
        run_bootstrap_command(["rm", "-rf", VENV_DIR], "Removing old virtual environment...")
    run_bootstrap_command([sys.executable, "-m", "venv", VENV_DIR], "Creating fresh virtual environment...")

    python_executable = os.path.join(VENV_DIR, "bin", "python")

    # Install the local project in editable mode.
    # pip will read pyproject.toml and install all dependencies automatically.
    install_cmd = [python_executable, "-m", "pip", "install", "-e", "."]
    run_bootstrap_command(install_cmd, "Installing project dependencies...")

    print("\n🚀 Bootstrap complete. Launching application...\n")

    # Set environment for the final execution
    os.environ['PATH'] = os.path.join(VENV_DIR, 'bin') + os.pathsep + os.environ['PATH']
    os.environ['VIRTUAL_ENV'] = VENV_DIR

    # Execute the separate run.py script
    os.execv(python_executable, [python_executable, RUN_SCRIPT])