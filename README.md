# OS Config Tool

A comprehensive automation tool for setting up Debian-based development environments with pre-configured packages, tools, and system configurations.

## 🚀 Features

### Package Management
- **Interactive Package Selection**: Choose from a curated list of development tools and applications
- **Smart Package Validation**: Automatically validates package names before installation
- **Custom Package Support**: Add additional packages beyond the default selection
- **Repository Management**: Sets up additional repositories for LibreWolf, VS Code, and Docker

### Development Environment Setup
- **Development Tools**: Build essentials, Git, Go, Node.js, and more
- **Code Editors**: VS Code, Neovim, Vim with configurations
- **Terminal Emulators**: Alacritty, Kitty, and Tmux with custom configurations
- **Version Control**: Git configuration with SSH key generation
- **Container Tools**: Docker CE with proper user group setup

### System Configuration
- **XFCE Desktop**: Custom desktop environment configuration
- **Browser Extensions**: Chromium extension installation
- **Security Tools**: SSH key generation, VPN support
- **Media & Productivity**: LibreOffice, GIMP, VLC, and more
- **Network Tools**: Wireshark, Nmap, OpenVPN

### User Experience
- **Interactive CLI**: User-friendly prompts using InquirerPy
- **Progress Tracking**: Real-time status updates with spinners
- **Comprehensive Logging**: Detailed setup logs for troubleshooting
- **Error Handling**: Graceful fallbacks and user notifications

## 📋 Prerequisites

- **Operating System**: Debian-based Linux distribution (Debian, Ubuntu, Linux Mint, etc.)
- **Permissions**: Root/sudo access required
- **Python**: Python 3.7+ (automatically handled by the tool)
- **Internet Connection**: Required for package downloads and installations

## 🛠️ Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd os-config

# Run the installer (will automatically request sudo if needed)
python3 install.py
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the setup
python3 run.py
```

## 🎯 Usage

### Basic Setup
1. **Run the installer**: `python3 install.py`
2. **Follow the prompts**: Select packages and configurations
3. **Wait for completion**: The tool handles everything automatically

### Package Selection
- **Default Packages**: Pre-selected essential development tools
- **Custom Packages**: Add additional packages during installation
- **Validation**: Automatic package name validation
- **Dependencies**: Automatic dependency resolution

### Configuration Options
- **SSH Keys**: Generate new SSH keys or use existing ones
- **Git Setup**: Configure Git with your credentials
- **Docker**: Add user to docker group for non-sudo access
- **Desktop**: Customize XFCE desktop environment
- **Terminal**: Configure Tmux with custom theme and shortcuts

## 📁 Project Structure

```
os-config/
├── install.py          # Main installer script
├── run.py              # Setup execution script
├── pyproject.toml      # Project dependencies and metadata
├── src/                # Source code
│   ├── main.py         # Main setup orchestration
│   ├── packages.py     # Package management logic
│   ├── configure.py    # System configuration functions
│   ├── repositories.py # Repository setup
│   ├── utils.py        # Utility functions
│   └── cursor.sh       # Cursor editor installer
├── tmux/               # Tmux configuration
│   └── tmux.conf       # Custom tmux theme and settings
└── README.md           # This file
```

## 🔧 Dependencies

### Core Dependencies
- **InquirerPy**: Interactive command-line prompts
- **yaspin**: Terminal spinners for progress indication

### System Dependencies
- **apt**: Package management
- **fuse**: AppImage support
- **build-essential**: Compilation tools

## 📝 Default Package List

### Development Tools
- `build-essential`, `git`, `golang-go`
- `code` (VS Code), `neovim`, `vim`
- `docker-ce`, `docker-compose-plugin`

### Terminal & Shell
- `alacritty`, `kitty`, `tmux`
- `htop`, `bat`, `fd-find`

### Productivity
- `libreoffice`, `gimp`, `obs-studio`
- `keepassxc`, `qbittorrent`, `vlc`

### Security & Network
- `wireshark`, `nmap`, `openvpn`
- `network-manager-openvpn-gnome`

## 🎨 Customization

### Adding Custom Packages
```bash
# During installation, you'll be prompted for additional packages
# Enter space-separated package names
firefox thunderbird libreoffice-calc
```

### Modifying Default Packages
Edit `src/packages.py` to modify the `default_package_names` list.

### Custom Tmux Configuration
Modify `tmux/tmux.conf` to customize your terminal multiplexer setup.

## 🐛 Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure you're running with sudo
2. **Package Not Found**: Check package names and internet connection
3. **Installation Failures**: Check `setup.log` for detailed error information

### Logs
- **Setup Log**: `setup.log` contains detailed installation information
- **Verbose Mode**: Use logging for debugging package installations

### Recovery
- The tool is designed to be re-runnable
- Failed installations can be retried
- Already installed packages are automatically detected

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd os-config
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Adding Features
1. **New Packages**: Add to `default_package_names` in `packages.py`
2. **New Configurations**: Extend `configure.py` with new functions
3. **UI Improvements**: Enhance prompts in the main modules

### Testing
- Test on fresh Debian-based systems
- Verify package compatibility
- Check error handling scenarios

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- **Debian/Ubuntu**: Base system compatibility
- **InquirerPy**: Interactive CLI framework
- **Open Source Community**: Package maintainers and contributors

---

**Note**: This tool is designed for development environments. Always review package selections and configurations before running on production systems.