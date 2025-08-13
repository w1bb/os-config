import os
import shutil
import subprocess
import json
import logging
import pwd
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from .utils import run_command, run_command_as_user
from .packages import is_package_installed

LOG_FILE = "setup.log"

def configure_docker_group():
    """Adds the user to the docker group to run docker without sudo."""
    if not is_package_installed("docker-ce"):
        return
        
    user = get_real_user()
    if not user:
        return
        
    print("\n--- Docker Post-Installation ---")
    try:
        configure = inquirer.confirm(
            message=f"Do you want to add user '{user}' to the 'docker' group?\n"
                    f" (This allows running docker commands without sudo)",
            default=True
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nDocker group configuration cancelled.")
        return
        
    if configure:
        if run_command(["usermod", "-aG", "docker", user], f"Adding user {user} to docker group..."):
            print("\n✅ IMPORTANT: You must log out and log back in for the new group permissions to take effect.")
        else:
            print("❌ Failed to add user to the docker group.")

def install_cursor_editor():
    """Asks to run the guided installer for the Cursor editor."""
    user = get_real_user()
    if not user:
        return

    print("\n--- Cursor Editor Installation ---")
    script_path = os.path.abspath("src/cursor.sh")

    if not os.path.exists(script_path):
        logging.error(f"Cursor installation script not found at {script_path}")
        print(f"❌ Error: Cursor installation script not found!")
        return
        
    try:
        install = inquirer.confirm(
            message="Do you want to open the guided installer for the Cursor editor?",
            default=False
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nCursor installation cancelled.")
        return

    if install:
        print("\nChecking for AppImage dependency: fuse...")
        if not is_package_installed("fuse") or not is_package_installed("libfuse2"):
            if not run_command(["apt", "install", "-y", "fuse", "libfuse2"], "Installing fuse..."):
                print("❌ Warning: Failed to install 'fuse'. The AppImage may not run correctly.")
                logging.error("Failed to install the 'fuse' package, but continuing.")
        else:
            print("✅ 'fuse' is already installed.")
        try:
            # Make the script executable
            os.chmod(script_path, 0o755)
            logging.info(f"Made {script_path} executable.")

            # Run the script as the original user in an interactive session
            print("Launching the guided installer...")
            subprocess.run(["sudo", "-u", user, script_path])
            
        except Exception as e:
            logging.error(f"Failed to run Cursor installation script: {e}")
            print(f"❌ An error occurred while trying to launch the script. Check {LOG_FILE}.")

def get_real_user():
    """Gets the original user who ran the script with sudo."""
    user = os.environ.get('SUDO_USER')
    if not user:
        logging.warning("SUDO_USER not set. Some user-specific configurations may be skipped.")
    return user

def generate_ssh_keys():
    """Asks to generate SSH keys if they don't exist."""
    user = get_real_user()
    if not user:
        return

    home_dir = os.path.expanduser(f"~{user}")
    ssh_key_path = os.path.join(home_dir, ".ssh", "id_rsa")

    if os.path.exists(ssh_key_path):
        print(f"✅ SSH key already exists at {ssh_key_path}. Skipping generation.")
        logging.info(f"SSH key found for user {user}. Skipping.")
        return

    print("\n--- SSH Key Generation ---")
    try:
        generate = inquirer.confirm(
            message="No SSH key found. Do you want to generate one now?",
            default=True
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nSSH key generation cancelled.")
        return
        
    if generate:
        ssh_dir = os.path.join(home_dir, ".ssh")
        # Ensure .ssh directory exists with correct permissions
        run_command_as_user(user, [f"mkdir -p {ssh_dir}", f"&& chmod 700 {ssh_dir}"], "Creating .ssh directory...")
        
        # Generate key non-interactively
        command = [
            "ssh-keygen",
            "-t", "rsa",
            "-b", "4096",
            "-f", ssh_key_path,
            "-N", '""' # Pass an empty passphrase
        ]
        run_command_as_user(user, command, "Generating 4096-bit RSA SSH key...")

def setup_git_config():
    """Prompts to set up global git username and email if not configured."""
    user = get_real_user()
    if not user:
        return
        
    try:
        name_cmd = f"sudo -u {user} git config --global user.name"
        email_cmd = f"sudo -u {user} git config --global user.email"
        name = subprocess.check_output(name_cmd, shell=True, text=True).strip()
        email = subprocess.check_output(email_cmd, shell=True, text=True).strip()
        if name and email:
            print("✅ Git user.name and user.email are already configured. Skipping.")
            logging.info("Git config is already set.")
            return
    except subprocess.CalledProcessError:
        # This is expected if the config values are not set
        pass

    print("\n--- Git Configuration ---")
    try:
        configure = inquirer.confirm(
            message="Git user details are not set. Do you want to configure them now?",
            default=True
        ).execute()
        if not configure:
            return

        git_name = inquirer.text(message="Enter your Git username:", default=user).execute()
        git_email = inquirer.text(message="Enter your Git email address:").execute()

    except (KeyboardInterrupt, TypeError):
        print("\nGit configuration cancelled.")
        return

    if git_name:
        run_command_as_user(user, [f"git config --global user.name '{git_name}'"], "Setting Git username...")
    if git_email:
        run_command_as_user(user, [f"git config --global user.email '{git_email}'"], "Setting Git email...")

def setup_tmux_config():
    """Asks to install a custom tmux configuration."""
    if not is_package_installed("tmux"):
        return
        
    user = get_real_user()
    if not user:
        return

    print("\n--- Tmux Configuration ---")
    try:
        configure = inquirer.confirm(
            message="Do you want to install the recommended tmux configuration?",
            default=True
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nTmux configuration cancelled.")
        return
        
    if configure:
        user_info = pwd.getpwnam(user)
        user_uid = user_info.pw_uid
        user_gid = user_info.pw_gid

        source_path = os.path.abspath("config/tmux/tmux.conf")
        if not os.path.exists(source_path):
            logging.error(f"Tmux config source file not found at {source_path}")
            print(f"❌ Error: Tmux config source file not found!")
            return

        home_dir = os.path.expanduser(f"~{user}")
        dest_dir = os.path.join(home_dir, ".config", "tmux")
        dest_path = os.path.join(dest_dir, "tmux.conf")
        
        print(f"Copying tmux config to {dest_path}...")
        
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(source_path, dest_path)
        
        # Set correct ownership for the entire .config/tmux directory
        os.chown(dest_dir, user_uid, user_gid)
        os.chown(dest_path, user_uid, user_gid)
        
        print("✅ Tmux configuration applied.")
        logging.info(f"Copied tmux config for user {user}.")

def configure_xfce():
    """Asks and applies XFCE specific configurations."""
    sudo_user = os.environ.get('SUDO_USER')
    desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

    if 'xfce' not in desktop_env:
        print("\nℹ️  Skipping XFCE configuration because the current desktop is not XFCE.")
        logging.info(f"Skipping XFCE config, XDG_CURRENT_DESKTOP is '{desktop_env}'")
        return

    if not sudo_user:
        print("\n⚠️  Skipping XFCE configuration: Could not determine the original user (SUDO_USER not set).")
        logging.warning("Cannot apply XFCE user settings without SUDO_USER.")
        return

    if not shutil.which('xfconf-query'):
        print("\n⚠️  Skipping XFCE configuration: 'xfconf-query' command not found.")
        logging.warning("Cannot apply XFCE settings, 'xfconf-query' not in PATH.")
        return

    # --- Get the user's DBus and Display environment ---
    user_env = os.environ.copy()
    try:
        pid = subprocess.check_output(
            ["pgrep", "-u", sudo_user, "xfce4-session"],
            text=True
        ).strip().split("\n")[0]
        with open(f"/proc/{pid}/environ", "rb") as f:
            environ_data = f.read().decode("utf-8").split("\x00")
        for entry in environ_data:
            if entry.startswith("DBUS_SESSION_BUS_ADDRESS=") or entry.startswith("DISPLAY="):
                key, value = entry.split("=", 1)
                user_env[key] = value
        logging.info(f"XFCE session env for {sudo_user}: DBUS={user_env.get('DBUS_SESSION_BUS_ADDRESS')} DISPLAY={user_env.get('DISPLAY')}")
    except Exception as e:
        logging.error(f"Failed to get XFCE session environment for {sudo_user}: {e}")
        print(f"\n⚠️  Could not get XFCE session environment for {sudo_user}. Settings may not apply to the live session.")

    def run_xfce_query(args, spinner_text):
        """Runs xfconf-query as the target user with correct env."""
        base_cmd = ["sudo", "-u", sudo_user, "env"] + \
                   [f"{k}={v}" for k, v in user_env.items() if k in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")]
        return run_command(base_cmd + args, spinner_text=spinner_text)

    settings_changed = False
    print(f"\n--- XFCE Configuration for user '{sudo_user}' ---")

    # 1. Change theme
    try:
        change_theme = inquirer.confirm(
            message="Do you want to change the theme to Adwaita-dark?",
            default=True
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nTheme selection cancelled.")
        change_theme = False

    if change_theme:
        if run_command(
            ["sudo", "-u", sudo_user, "env"] +
            [f"{k}={v}" for k, v in user_env.items() if k in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")] +
            ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", "Adwaita-dark"],
            "Changing theme to Adwaita-dark..."
        ):
            settings_changed = True

    # 2. Change Ctrl+Alt+T terminal shortcut
    terminal_choices = [Choice(value="current", name="Keep current terminal")]
    default_terminal = "current"

    if is_package_installed("kitty"):
        terminal_choices.append(Choice(value="kitty", name="kitty"))
        default_terminal = "kitty"
    if is_package_installed("alacritty"):
        terminal_choices.append(Choice(value="alacritty", name="Alacritty"))
        if default_terminal == "current":
            default_terminal = "alacritty"

    if len(terminal_choices) > 1:
        try:
            chosen_terminal = inquirer.select(
                message="Select the terminal to launch with Ctrl+Alt+T:",
                choices=terminal_choices,
                default=default_terminal,
                cycle=True
            ).execute()
        except (KeyboardInterrupt, TypeError):
            print("\nTerminal selection cancelled.")
            chosen_terminal = "current"

        if chosen_terminal != "current":
            if run_command(
                ["sudo", "-u", sudo_user, "env"] +
                [f"{k}={v}" for k, v in user_env.items() if k in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")] +
                [
                    "xfconf-query", "-c", "xfce4-keyboard-shortcuts",
                    "-p", "/commands/custom/<Primary><Alt>t",
                    "--create", "-t", "string", "-s", chosen_terminal
                ],
                f"Setting Ctrl+Alt+T to launch {chosen_terminal}..."
            ):
                settings_changed = True

    # 3. Rofi keybind
    if is_package_installed("rofi"):
        print("\n--- Rofi Shortcut Configuration ---")
        try:
            override_rofi = inquirer.confirm(
                message="Do you want to set Meta+P to launch Rofi (application launcher)?",
                default=True
            ).execute()
        except (KeyboardInterrupt, TypeError):
            print("\nRofi shortcut configuration cancelled.")
            override_rofi = False
        
        if override_rofi:
            # Find and disable any existing bindings for <Super>p
            # This key is often used by xfwm4 for display settings.
            try:
                list_cmd = ['sudo', '-u', sudo_user, 'env'] + \
                           [f"{k}={v}" for k, v in user_env.items() if k in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")] + \
                           ['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-l']
                
                result = subprocess.run(list_cmd, capture_output=True, text=True, check=True)
                all_shortcuts = result.stdout.strip().split('\n')
                
                super_p_shortcuts = [s for s in all_shortcuts if s.endswith('/<Super>p')]

                if super_p_shortcuts:
                    logging.info(f"Found existing shortcuts for <Super>p: {super_p_shortcuts}")
                    for prop in super_p_shortcuts:
                        if run_xfce_query(
                            ['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', prop, '-r'],
                            f"Disabling old shortcut bound to Meta+P..."
                        ):
                            settings_changed = True
                else:
                    logging.info("No existing shortcuts found for <Super>p.")

            except Exception as e:
                logging.error(f"An error occurred while searching for existing shortcuts: {e}")
            
            # Create the new Rofi shortcut
            if run_xfce_query(
                [
                    'xfconf-query', '-c', 'xfce4-keyboard-shortcuts',
                    '-p', '/commands/custom/<Super>p',
                    '--create', '-t', 'string', '-s', 'rofi -show drun'
                ],
                "Binding Meta+P to 'rofi -show drun'..."
            ):
                settings_changed = True

    # 4. Reload settings if changed
    if settings_changed:
        os.sync()
        print("\nApplying XFCE settings...")
        try:
            pgrep_cmd = ['pgrep', '-u', sudo_user, '-x', 'xfsettingsd']
            result = subprocess.run(pgrep_cmd, capture_output=True, text=True, check=True)
            pid = result.stdout.strip().split('\n')[0]

            if pid:
                logging.info(f"Found PID: {pid}. Sending SIGHUP to reload configuration.")
                if run_command(['kill', '-HUP', pid], "Reloading XFCE settings daemon..."):
                    print("✅ Settings reloaded. Changes should now be active.")
                else:
                    print("⚠️  Could not reload the XFCE settings daemon. Logout/login may be required.")
            else:
                print("⚠️  Could not find the XFCE settings daemon. Logout/login may be required.")

        except subprocess.CalledProcessError:
            logging.error("pgrep failed to find 'xfsettingsd' for the user.")
            print("⚠️  Could not find the XFCE settings daemon. Logout/login may be required.")
        except Exception as e:
            logging.error(f"Error while reloading XFCE settings: {e}")
            print("⚠️  Error applying settings. Logout/login may be required.")

def install_chromium_extensions():
    """Asks to install selected Chromium extensions via managed policies."""
    if not is_package_installed("chromium"):
        return

    print("\n--- Chromium Extension Setup ---")

    extensions = {
        "uBlock Origin Lite": "ddkjiahejlhfcafbddmgiahcphecmpfh"
    }

    try:
        selected_extensions = inquirer.checkbox(
            message="Select Chromium extensions to install (optional):",
            choices=[Choice(value=ext_id, name=ext_name, enabled=True) for ext_name, ext_id in extensions.items()],
            cycle=True
        ).execute()
    except (KeyboardInterrupt, TypeError):
        print("\nExtension selection cancelled.")
        return

    if not selected_extensions:
        print("No extensions selected.")
        return

    policy_dir = "/etc/chromium/policies/managed"
    policy_file = os.path.join(policy_dir, "zz_managed_extensions.json")

    print(f"Configuring extensions in {policy_file}...")

    install_list = [f"{ext_id};https://clients2.google.com/service/update2/crx" for ext_id in selected_extensions]
    policy_json = {"ExtensionInstallForcelist": install_list}

    try:
        os.makedirs(policy_dir, exist_ok=True)
        logging.info(f"Ensured directory exists: {policy_dir}")

        with open(policy_file, 'w') as f:
            json.dump(policy_json, f, indent=4)

        logging.info(f"Wrote Chromium extension policy to {policy_file}")
        print("✅ Successfully configured Chromium extensions.")
        print("   (Note: A browser restart is required for changes to take effect)")

    except Exception as e:
        logging.error(f"Failed to write Chromium policy file: {e}")
        print(f"❌ An error occurred while configuring extensions. Check {LOG_FILE}.")