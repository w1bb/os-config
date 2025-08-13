import logging
import subprocess
import sys
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
# Import the new function
from .utils import run_command, run_verbose_command
from .repositories import setup_librewolf_repo, setup_vscode_repo, setup_docker_repo

def is_package_installed(package_name):
    """Checks if a package is installed using dpkg."""
    logging.info(f"Checking installation status for package: {package_name}")
    status = subprocess.run(
        ['dpkg', '-s', package_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ).returncode
    is_installed = status == 0
    logging.info(f"Status for {package_name}: {'Installed' if is_installed else 'Not Installed'}")
    return is_installed

def validate_package_names(package_names):
    """Checks if package names exist in apt-cache. Returns valid and invalid lists."""
    valid = []
    invalid = []
    if not package_names:
        return [], []

    logging.info(f"Validating packages: {', '.join(package_names)}")
    for name in package_names:
        if not name: continue
        result = subprocess.run(
            ['apt-cache', 'show', name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            valid.append(name)
        else:
            invalid.append(name)
    logging.info(f"Validation result -> Valid: {valid}, Invalid: {invalid}")
    return valid, invalid

def handle_package_installation():
    """Handles the entire package selection and installation process."""
    print("\n--- Package Installation ---")

    last_selected_packages = None
    last_additional_packages_str = ""
    final_package_list = []

    while True:
        default_package_names = [
            "alacritty", "bat", "build-essential", "chromium", "code", "docker-ce", 
            "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin",
            "fd-find", "gimp", "git", "golang-go", "htop", "jq", "keepassxc", "kitty",
            "libreoffice", "librewolf", "neovim", "network-manager-openvpn-gnome", "nmap",
            "openvpn", "obs-studio", "pandoc", "qbittorrent", "rofi", "tmux", "unzip", "vim",
            "vlc", "wireshark"
        ]
        choices = []
        print("\nChecking package statuses...")
        for pkg in sorted(list(set(default_package_names))):
            if is_package_installed(pkg):
                choices.append(Choice(value=pkg, name=f"{pkg} (already installed)", enabled=False))
            else:
                is_enabled_by_default = (pkg != "alacritty")
                choices.append(Choice(value=pkg, name=pkg, enabled=is_enabled_by_default))

        if last_selected_packages is not None:
            pre_selected_set = set(last_selected_packages)
            for choice in choices:
                if not choice.name.endswith("(already installed)"):
                    choice.enabled = choice.value in pre_selected_set

        try:
            current_selected_packages = inquirer.checkbox(
                message="Select packages to install (Space to toggle, Enter to confirm):",
                choices=choices, cycle=True
            ).execute()

            current_additional_packages_str = last_additional_packages_str
            while True:
                current_additional_packages_str = inquirer.text(
                    message="Enter additional space-separated packages to install (or press Enter to skip):",
                    default=current_additional_packages_str
                ).execute()

                additional_packages = list(filter(None, current_additional_packages_str.split()))
                if not additional_packages:
                    break

                valid, invalid = validate_package_names(additional_packages)
                if not invalid:
                    break

                print(f"\n❌ The following packages were not found: {', '.join(invalid)}")
                current_additional_packages_str = " ".join(valid)

        except (KeyboardInterrupt, TypeError):
            print("\n\nSelection cancelled by user. Exiting.")
            sys.exit(0)

        last_selected_packages = current_selected_packages
        last_additional_packages_str = current_additional_packages_str

        additional_packages = list(filter(None, last_additional_packages_str.split()))
        final_package_list = sorted(list(set(last_selected_packages + additional_packages)))

        if not final_package_list:
            print("No new packages selected to install.")
            if inquirer.confirm(message="Do you want to select packages again?", default=False).execute():
                continue
            else:
                break

        print("\nPackages to be installed:")
        for pkg in final_package_list: print(f"- {pkg}")

        if inquirer.confirm(message="Do you want to install these packages?", default=True).execute():
            break
        else:
            print("Package selection cancelled. Please select again.\n")
            continue

    # --- Pre-installation Setup for Special Repositories ---
    needs_repo_update = False
    if 'librewolf' in final_package_list and not is_package_installed('librewolf'):
        if setup_librewolf_repo():
            needs_repo_update = True
    if 'code' in final_package_list and not is_package_installed('code'):
        if setup_vscode_repo():
            needs_repo_update = True
    if 'docker-ce' in final_package_list and not is_package_installed('docker-ce'):
        if setup_docker_repo():
            needs_repo_update = True

    if needs_repo_update:
        print("\n--- Updating package lists after adding repositories ---")
        if not run_command(["apt", "update", "-y"], "Updating package lists..."):
            print("\n❌ Failed to update package lists. Installation may fail.")
            sys.exit(1)

    # --- Main Installation Step ---
    if final_package_list:
        install_command = ["apt", "install", "-y"] + final_package_list
        # Use the new verbose function for this long-running command
        if not run_verbose_command(install_command, f"Installing {len(final_package_list)} selected packages..."):
            print("\n❌ Package installation failed. Check setup.log for details.")
            sys.exit(1)

    return True