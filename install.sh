#!/usr/bin/env bash
#
# install.sh - Installer for nautilus-sidebar-separators
# https://github.com/m4rco-m/nautilus-sidebar-separators
#
set -euo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RED="\033[31m"
RESET="\033[0m"

log_info() {
    echo -e "${CYAN}==>${RESET} ${BOLD}$1${RESET}"
}

log_success() {
    echo -e "${GREEN}✔${RESET} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

log_error() {
    echo -e "${RED}✖${RESET} $1" >&2
}

echo -e "${BOLD}=========================================${RESET}"
echo -e "${BOLD}   Nautilus Sidebar Separators Installer  ${RESET}"
echo -e "${BOLD}=========================================${RESET}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSIONS_DIR="${HOME}/.local/share/nautilus-python/extensions"
SEPARATORS_DIR="${HOME}/.local/share/nautilus-separators"
BIN_DIR="${HOME}/.local/bin"

# 1. Check Python 3 and GObject Introspection / nautilus-python
log_info "Checking system requirements..."

if ! command -v python3 &>/dev/null; then
    log_error "Python 3 is required but could not be found."
    exit 1
fi

check_nautilus_python() {
    python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Nautilus" &>/dev/null
}

if check_nautilus_python; then
    log_success "nautilus-python is already installed and functional."
else
    log_warn "nautilus-python not detected in Python path. Attempting package installation..."

    # Detect package manager
    PKG_INSTALLED=false

    if [ -f /etc/os-release ]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        OS_ID="${ID:-}"
        OS_LIKE="${ID_LIKE:-}"
    else
        OS_ID="unknown"
        OS_LIKE=""
    fi

    SUDO_CMD=""
    if [ "$(id -u)" -ne 0 ]; then
        if command -v sudo &>/dev/null; then
            SUDO_CMD="sudo"
        else
            log_warn "sudo not available; please ensure you have root privileges."
        fi
    fi

    if [[ "$OS_ID" =~ (fedora|rhel|centos|rocky|almalinux) ]] || [[ "$OS_LIKE" =~ (fedora|rhel) ]]; then
        log_info "Detected Fedora/RHEL-based system. Installing nautilus-python via dnf..."
        $SUDO_CMD dnf install -y nautilus-python || true
    elif [[ "$OS_ID" =~ (ubuntu|debian|pop|linuxmint|elementary) ]] || [[ "$OS_LIKE" =~ (ubuntu|debian) ]]; then
        log_info "Detected Debian/Ubuntu-based system. Installing python3-nautilus via apt..."
        $SUDO_CMD apt-get update && $SUDO_CMD apt-get install -y python3-nautilus || true
    elif [[ "$OS_ID" =~ (arch|manjaro|endeavouros) ]] || [[ "$OS_LIKE" =~ (arch) ]]; then
        log_info "Detected Arch-based system. Installing python-nautilus via pacman..."
        $SUDO_CMD pacman -S --noconfirm python-nautilus || true
    elif [[ "$OS_ID" =~ (opensuse|sles) ]] || [[ "$OS_LIKE" =~ (suse) ]]; then
        log_info "Detected openSUSE system. Installing python3-nautilus via zypper..."
        $SUDO_CMD zypper install -y python3-nautilus || true
    else
        log_warn "Unrecognized Linux distribution: $OS_ID. Please install 'nautilus-python' or 'python3-nautilus' manually."
    fi

    if check_nautilus_python; then
        log_success "nautilus-python dependency resolved."
    else
        log_warn "Could not verify nautilus-python automatically."
        log_warn "If Nautilus fails to load the extension, please install the package manually:"
        log_warn "  - Fedora: sudo dnf install nautilus-python"
        log_warn "  - Ubuntu/Debian: sudo apt install python3-nautilus"
        log_warn "  - Arch: sudo pacman -S python-nautilus"
    fi
fi

# 2. Create destination directories
log_info "Setting up directories..."
mkdir -p "${EXTENSIONS_DIR}"
mkdir -p "${SEPARATORS_DIR}"
mkdir -p "${BIN_DIR}"
log_success "Directories created in ~/.local/share and ~/.local/bin"

# 3. Install Nautilus extension
log_info "Installing Nautilus extension..."
cp "${SCRIPT_DIR}/src/sidebar_separators.py" "${EXTENSIONS_DIR}/sidebar_separators.py"
chmod +r "${EXTENSIONS_DIR}/sidebar_separators.py"
log_success "Extension copied to ${EXTENSIONS_DIR}/sidebar_separators.py"

# 4. Install CLI utility
log_info "Installing CLI tool (nautilus-separator)..."
cp "${SCRIPT_DIR}/bin/nautilus-separator" "${BIN_DIR}/nautilus-separator"
chmod +x "${BIN_DIR}/nautilus-separator"
log_success "CLI tool installed to ${BIN_DIR}/nautilus-separator"

# 5. Check PATH for ~/.local/bin
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    echo ""
    log_warn "${BIN_DIR} is not currently in your PATH environment variable."
    echo -e "   To run ${BOLD}nautilus-separator${RESET} from anywhere, add this to your shell profile (~/.bashrc or ~/.zshrc):"
    echo -e "   ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo ""
fi

# 6. Restart Nautilus
log_info "Restarting Nautilus to apply changes..."
if command -v nautilus &>/dev/null; then
    nautilus -q || true
    log_success "Nautilus restarted."
else
    log_warn "Nautilus executable not found in PATH. Please restart your file manager manually."
fi

echo ""
echo -e "${GREEN}${BOLD}Installation completed successfully!${RESET}"
echo ""
echo -e "Get started by adding your first separator header:"
echo -e "  ${CYAN}nautilus-separator add \"PROJECTS\"${RESET}"
echo -e "  ${CYAN}nautilus-separator add \"WORK\"${RESET}"
echo -e "  ${CYAN}nautilus-separator list${RESET}"
echo ""
echo -e "You can drag and reorder separators and bookmarks directly inside the Nautilus sidebar!"
