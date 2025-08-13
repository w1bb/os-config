import logging
import os
import subprocess
from yaspin import yaspin
from yaspin.spinners import Spinners
from .utils import run_command

def setup_docker_repo():
    """
    Adds Docker's official GPG key and APT repository.
    This follows the official installation documentation.
    """
    print("\n--- Configuring Docker Repository ---")
    
    # 1. Install prerequisite packages
    if not run_command(
        ["apt-get", "install", "-y", "ca-certificates", "curl"],
        "Installing dependencies for Docker repository (curl)..."
    ):
        logging.error("Failed to install prerequisites for Docker repo.")
        return False

    # 2. Add Docker's official GPG key
    keyring_dir = "/etc/apt/keyrings"
    keyring_path = os.path.join(keyring_dir, "docker.asc")
    
    if not run_command(["install", "-m", "0755", "-d", keyring_dir], "Creating keyring directory..."):
        logging.error("Failed to create apt keyring directory.")
        return False

    curl_cmd = [
        "curl", "-fsSL", "https://download.docker.com/linux/debian/gpg",
        "-o", keyring_path
    ]
    if not run_command(curl_cmd, "Downloading Docker GPG key..."):
        logging.error("Failed to download Docker GPG key.")
        return False

    if not run_command(["chmod", "a+r", keyring_path], "Setting key permissions..."):
        logging.error("Failed to set permissions on Docker GPG key.")
        return False
        
    # 3. Add the repository to Apt sources
    try:
        arch = subprocess.check_output(["dpkg", "--print-architecture"], text=True).strip()
        os_release_cmd = ". /etc/os-release && echo \"$VERSION_CODENAME\""
        codename = subprocess.check_output(os_release_cmd, shell=True, text=True).strip()
        
        repo_string = (
            f"deb [arch={arch} signed-by={keyring_path}] "
            f"https://download.docker.com/linux/debian {codename} stable"
        )
        
        with open("/etc/apt/sources.list.d/docker.list", 'w') as f:
            f.write(repo_string + "\n")
            
        print("✅ Docker repository source file created.")
        logging.info("Successfully wrote Docker repo config.")
        
    except Exception as e:
        print(f"❌ Failed to create Docker repository file: {e}")
        logging.error(f"Failed to create docker.list: {e}")
        return False

    return True

def setup_vscode_repo():
    """
    Adds the Microsoft GPG key and repository for VSCode.
    This function follows the official installation documentation.
    """
    print("\n--- Configuring VSCode Repository ---")

    # 1. Install prerequisite packages
    if not run_command(
        ["apt-get", "install", "-y", "wget", "gpg", "apt-transport-https"],
        "Installing dependencies for VSCode repository (wget, gpg)..."
    ):
        logging.error("Failed to install prerequisites for VSCode repo.")
        return False

    # 2. Download and install the Microsoft GPG key
    keyring_path = "/usr/share/keyrings/microsoft-vscode-keyring.gpg"
    temp_key_file = "microsoft.gpg"

    wget_cmd = f"wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > {temp_key_file}"
    logging.info(f"Executing GPG download command: {wget_cmd}")

    sp = yaspin(Spinners.dots, text="Downloading VSCode GPG key...")
    sp.start()
    result = subprocess.run(wget_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        sp.fail("❌")
        logging.error(f"Failed to download or dearmor GPG key. Stderr: {result.stderr}")
        return False
    sp.ok("✅")

    if not run_command(
        ["install", "-D", "-o", "root", "-g", "root", "-m", "644", temp_key_file, keyring_path],
        "Installing VSCode GPG key..."
    ):
        logging.error("Failed to install GPG key using `install` command.")
        run_command(["rm", "-f", temp_key_file], "Cleaning up temporary key file...")
        return False

    run_command(["rm", "-f", temp_key_file], "Cleaning up temporary key file...")

    # 3. Create the repository sources file
    repo_file_path = "/etc/apt/sources.list.d/vscode.sources"
    repo_content = f"""Types: deb
URIs: https://packages.microsoft.com/repos/code
Suites: stable
Components: main
Architectures: amd64,arm64,armhf
Signed-By: {keyring_path}
"""
    try:
        with open(repo_file_path, 'w') as f:
            f.write(repo_content)
        print("✅ VSCode repository source file created.")
        logging.info(f"Successfully wrote VSCode repo config to {repo_file_path}")
    except IOError as e:
        print(f"❌ Failed to create repository file: {e}")
        logging.error(f"Failed to create {repo_file_path}: {e}")
        return False

    return True

def setup_librewolf_repo():
    """Installs extrepo and enables the LibreWolf repository."""
    print("\n--- Configuring LibreWolf Repository ---")
    if not run_command(
        ["apt-get", "install", "-y", "extrepo"],
        "Installing extrepo..."
    ): return False

    if not run_command(
        ["extrepo", "enable", "librewolf"],
        "Enabling LibreWolf repository..."
    ): return False

    return True