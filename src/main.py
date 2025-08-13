import os
import sys
import logging
from .utils import run_command
from .packages import handle_package_installation
from .configure import (
    configure_xfce,
    install_chromium_extensions,
    generate_ssh_keys,
    setup_git_config,
    setup_tmux_config,
    install_cursor_editor,
    configure_docker_group
)

LOG_FILE = "setup.log"

def run_debian_setup():
    """
    The main execution flow for setting up a Debian-based system.
    """
    # Re-initialize logging to append to the log file.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, mode='a')],
        force=True
    )

    if not os.path.exists('/etc/debian_version'):
        print("❌ This system does not appear to be Debian-based. Exiting.")
        sys.exit(1)

    print("✅ This system appears to be Debian-based.")

    print("\n--- Starting System Update ---")
    if run_command(["apt-get", "update", "-y"], "Updating package lists..."):
        run_command(["apt-get", "upgrade", "-y"], "Upgrading installed packages...")
    else:
        print("\n❌ Failed to update package lists. Check setup.log for details.")
        sys.exit(1)

    # Handle the entire package selection and installation process
    handle_package_installation()

    # --- Post-installation & Configuration Steps ---
    
    install_cursor_editor()
    generate_ssh_keys()
    setup_git_config()
    setup_tmux_config()
    configure_docker_group()
    configure_xfce()
    install_chromium_extensions()

    print("\n✅ Setup complete!")