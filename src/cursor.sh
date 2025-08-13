#!/usr/bin/env bash

# Brief: This script auto-generates and runs a temporary installer for Cursor IDE.
# It prompts for the AppImage URL, downloads the AppImage and icon, creates a desktop entry,
# sets up a launcher script, and updates the system caches — all without exiting your shell on errors.

# Create and run a temporary installer script for Cursor IDE

tmpfile=$(mktemp /tmp/cursor_installer.XXXXXX) || { echo "[ERROR] Failed to create temp file"; exit 1; }

cat << 'EOF' > "$tmpfile"
#!/usr/bin/env bash
# Exit on error, undefined var, or pipe failure
set -euo pipefail

# Log everything to console and log file
LOG_FILE="${HOME}/.cursor_install.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Pause on any error inside this installer
trap 'echo "[ERROR] Line $LINENO. See $LOG_FILE for details."; read -p "Press Enter to exit installer..."; exit 1' ERR

echo "[INFO] Starting Cursor IDE installation..."

# Prompt user for the AppImage download URL
echo "[TIP] You can find the latest download URL at:
  • https://github.com/oslook/cursor-ai-downloads
  • https://www.cursor.com/downloads"
read -p "Enter the Cursor AppImage download URL: " -r DOWNLOAD_URL
# Derive filename from URL
APPIMAGE_NAME=$(basename "$DOWNLOAD_URL")

# Installation directories
APP_DIR="${HOME}/Applications"
ICON_DIR="${HOME}/.local/share/icons"
DESKTOP_DIR="${HOME}/.local/share/applications"
BIN_DIR="${HOME}/.local/bin"
ICON_URL="https://www.cursor.com/brand/icon.svg"

# Paths
APPIMAGE_PATH="${APP_DIR}/${APPIMAGE_NAME}"
ICON_PATH="${ICON_DIR}/cursor-icon.svg"
DESKTOP_FILE_PATH="${DESKTOP_DIR}/cursor.desktop"
LAUNCHER_SCRIPT="${BIN_DIR}/cursor"

# Create necessary directories
mkdir -p "$APP_DIR" "$ICON_DIR" "$DESKTOP_DIR" "$BIN_DIR"

echo "[INFO] Ensuring curl is available..."
if ! command -v curl >/dev/null; then
  echo "[INFO] Installing curl..."
  sudo apt-get update && sudo apt-get install -y curl
else
  echo "[INFO] curl found."
fi

echo "[INFO] Downloading Cursor AppImage from $DOWNLOAD_URL..."
curl -fL "$DOWNLOAD_URL" -o "$APPIMAGE_PATH"
chmod +x "$APPIMAGE_PATH"
echo "[INFO] AppImage saved to $APPIMAGE_PATH"

# Download icon if not present
echo "[INFO] Checking icon..."
if [ ! -f "$ICON_PATH" ]; then
  curl -fsSL "$ICON_URL" -o "$ICON_PATH"
  echo "[INFO] Icon saved to $ICON_PATH"
else
  echo "[INFO] Icon already exists."
fi

# Write the .desktop entry
echo "[INFO] Writing desktop entry to $DESKTOP_FILE_PATH..."
cat > "$DESKTOP_FILE_PATH" << EOD
[Desktop Entry]
Name=Cursor IDE
Exec=$LAUNCHER_SCRIPT %F
Terminal=false
Type=Application
Icon=$ICON_PATH
StartupWMClass=Cursor
Comment=AI-first coding environment
Categories=Development;Utility;
MimeType=application/x-executable;
EOD
chmod +x "$DESKTOP_FILE_PATH"

echo "[INFO] Creating launcher script at $LAUNCHER_SCRIPT..."
printf '#!/usr/bin/env bash\nexec "${HOME}/Applications/%s" --no-sandbox "$@"\n' "$APPIMAGE_NAME" > "$LAUNCHER_SCRIPT"
chmod +x "$LAUNCHER_SCRIPT"

# Refresh desktop and icon caches if available
echo "[INFO] Updating desktop database and icon cache..."
command -v update-desktop-database >/dev/null && update-desktop-database "$DESKTOP_DIR" || echo "[WARN] update-desktop-database not available"
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -f -t "$ICON_DIR" || echo "[WARN] gtk-update-icon-cache not available"

echo "[INFO] Installation complete. Run 'cursor' in a new terminal to launch Cursor IDE."
EOF

# Execute installer and then clean up
bash "$tmpfile"
rm -f "$tmpfile"