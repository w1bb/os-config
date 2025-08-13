import logging
import subprocess
import os
from yaspin import yaspin
from yaspin.spinners import Spinners

LOG_FILE = "setup.log"

def run_command(command, spinner_text="Running command..."):
    """Runs a shell command with a spinner, logging the command and its output."""
    logging.info(f"Executing command: {' '.join(command)}")
    try:
        with yaspin(Spinners.dots, text=spinner_text) as sp:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace'
            )
            with process.stdout:
                for line in iter(process.stdout.readline, ""):
                    logging.info(line.strip())
            process.wait()

            if process.returncode == 0:
                sp.ok("✅")
                return True
            else:
                sp.fail("❌")
                logging.error(f"Command failed with return code {process.returncode}")
                return False
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

def run_verbose_command(command, message):
    """
    Runs a shell command and streams its output directly to the console.
    Ideal for long-running commands like apt-get install where progress is important.
    """
    logging.info(f"Executing verbose command: {' '.join(command)}")
    print(f"\n--- {message} ---")
    
    try:
        # Using Popen to stream output in real-time
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )

        # Read and print output line by line
        with process.stdout:
            for line in iter(process.stdout.readline, ""):
                print(line, end='') # Print to user's console
                logging.info(line.strip()) # Also write to log file
        
        process.wait()

        if process.returncode == 0:
            print("--- Command completed successfully --- ✅")
            return True
        else:
            print(f"--- Command failed with exit code {process.returncode} --- ❌")
            logging.error(f"Verbose command FAILED. See log for details.")
            return False

    except Exception as e:
        print(f"--- An unexpected error occurred: {e} --- ❌")
        logging.error(f"An unexpected error occurred during verbose command: {e}")
        return False


def run_command_as_user(user, command, spinner_text="Running command..."):
    """
    Runs a shell command as the specified user, preserving their home directory context.
    """
    if not user:
        logging.error("Cannot run command as user: user is not specified.")
        return False
        
    full_command = ["sudo", "-H", "-u", user, "bash", "-c", ' '.join(command)]
    return run_command(full_command, spinner_text)