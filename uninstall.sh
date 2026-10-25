#!/usr/bin/env bash
#
# uninstall.sh - Complete uninstaller for nautilus-sidebar-separators
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

echo -e "${BOLD}===========================================${RESET}"
echo -e "${BOLD}  Nautilus Sidebar Separators Uninstaller   ${RESET}"
echo -e "${BOLD}===========================================${RESET}"
echo ""

EXTENSIONS_FILE="${HOME}/.local/share/nautilus-python/extensions/sidebar_separators.py"
SEPARATORS_DIR="${HOME}/.local/share/nautilus-separators"
BIN_FILE="${HOME}/.local/bin/nautilus-separator"
BOOKMARKS_FILE="${HOME}/.config/gtk-3.0/bookmarks"

# 1. Clean bookmarks file using python
log_info "Cleaning separator entries from GTK bookmarks (~/.config/gtk-3.0/bookmarks)..."
if [ -f "${BOOKMARKS_FILE}" ]; then
    python3 - <<'EOF'
import os
from pathlib import Path

bookmarks_path = Path.home() / ".config" / "gtk-3.0" / "bookmarks"
sep_dir_str = "nautilus-separators"

if bookmarks_path.exists():
    try:
        lines = bookmarks_path.read_text(encoding="utf-8").splitlines()
        cleaned = []
        removed = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split(maxsplit=1)
            uri = parts[0]
            label = parts[1] if len(parts) > 1 else ""
            if sep_dir_str in uri or label.startswith("#"):
                removed += 1
            else:
                cleaned.append(stripped)
        
        content = "\n".join(cleaned)
        if content and not content.endswith("\n"):
            content += "\n"
        bookmarks_path.write_text(content, encoding="utf-8")
        print(f"Removed {removed} separator line(s) from GTK bookmarks.")
    except Exception as e:
        print(f"Warning: Failed to clean bookmarks: {e}")
EOF
    log_success "Bookmarks cleaned."
else
    log_info "Bookmarks file does not exist, skipping."
fi

# 2. Remove dummy folders
log_info "Removing dummy folder directory (${SEPARATORS_DIR})..."
if [ -d "${SEPARATORS_DIR}" ]; then
    rm -rf "${SEPARATORS_DIR}"
    log_success "Dummy directories removed."
else
    log_info "Dummy directory does not exist, skipping."
fi

# 3. Remove Nautilus extension
log_info "Removing Nautilus extension file..."
if [ -f "${EXTENSIONS_FILE}" ]; then
    rm -f "${EXTENSIONS_FILE}"
    log_success "Extension file removed."
else
    log_info "Extension file not found, skipping."
fi

# 4. Remove CLI utility
log_info "Removing CLI tool..."
if [ -f "${BIN_FILE}" ]; then
    rm -f "${BIN_FILE}"
    log_success "CLI binary removed."
else
    log_info "CLI binary not found, skipping."
fi

# 5. Restart Nautilus
log_info "Restarting Nautilus..."
if command -v nautilus &>/dev/null; then
    nautilus -q || true
    log_success "Nautilus restarted."
fi

echo ""
echo -e "${GREEN}${BOLD}Uninstallation complete!${RESET}"
echo -e "All files, separator bookmarks, and dummy folders have been cleanly removed."
