# Nautilus Sidebar Separators

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20GNOME%2043%2B-orange.svg)](#requirements)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#requirements)
[![Nautilus](https://img.shields.io/badge/Nautilus-43%20--%2049%2B-green.svg)](#requirements)

Organize your GNOME Files (**Nautilus 43+**) sidebar bookmarks with customizable, elegant section headers and horizontal dividers — complete with **native drag & drop** reordering.

```
       WITHOUT SEPARATORS                          WITH SEPARATORS
 ┌───────────────────────────┐              ┌───────────────────────────┐
 │ ★ Starred                 │              │ ★ Starred                 │
 │ ⌂ Home                    │              │ ⌂ Home                    │
 │ 🗁 Documents               │              │                           │
 │ 🗁 Downloads               │              │ WORK ───────────────────  │
 │ 🗁 Thesis                  │              │ 🗁 Thesis                  │
 │ 🗁 University              │              │ 🗁 University              │
 │ 🗁 Project Alpha           │              │                           │
 │ 🗁 Project Beta            │              │ PROJECTS ───────────────  │
 │ 🗁 Music                   │              │ 🗁 Project Alpha           │
 │ 🗁 Photos                  │              │ 🗁 Project Beta            │
 └───────────────────────────┘              └───────────────────────────┘
```

---

## Features

- 📑 **Custom Category Headers**: Group bookmarks cleanly under labeled section headers (`WORK`, `PROJECTS`, `MEDIA`, etc.).
- ➖ **Native GTK4 Horizontal Line**: Text label aligned to the left, followed by a subtle horizontal divider filling the remaining sidebar width.
- 🔀 **Native Drag & Drop**: Freely drag separators up and down in the sidebar alongside regular bookmarks to reorder your sections.
- 🚫 **Accidental Click Prevention**: Separator rows are non-activatable and non-selectable, preventing navigation into dummy folders.
- 🛠️ **CLI Management Tool (`nautilus-separator`)**: Add, list, and remove separators with a single command.
- 🎨 **Adwaita-Native Aesthetics**: Automatically respects system theme (Light & Dark mode) with subtle muted typography and clean line opacity.
- 🧩 **Zero Patching / Safe**: Runs cleanly as a standard `nautilus-python` extension without modifying system binaries or files.

---

## Demo

![Nautilus Sidebar Separators Demo](assets/preview.svg)

> 📹 **Live Demo Screencast**
>
> *(To capture and embed your own live recording: press `Ctrl+Alt+Shift+R` in GNOME to record a screencast, convert to GIF/MP4, and place it under `assets/demo.gif`)*

---

## Requirements

- **Linux Distribution**: Fedora, Ubuntu/Debian, Arch Linux, openSUSE, or any distro running GNOME 43 or later.
- **GNOME Files (Nautilus)**: Version 43, 44, 45, 46, 47, 48, or 49+.
- **Python**: 3.10+ (tested through Python 3.14).
- **nautilus-python**:
  - Fedora/RHEL: `nautilus-python`
  - Ubuntu/Debian/Pop!_OS: `python3-nautilus`
  - Arch Linux: `python-nautilus`
  - openSUSE: `python3-nautilus`

---

## Quick Installation

### One-line Install (Recommended)

Run the following command in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/m4rco-m/nautilus-sidebar-separators/main/install.sh | bash
```

### Manual Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/m4rco-m/nautilus-sidebar-separators.git
cd nautilus-sidebar-separators
./install.sh
```

The installer will:
1. Detect your package manager and ensure `nautilus-python` is installed.
2. Copy `src/sidebar_separators.py` to `~/.local/share/nautilus-python/extensions/`.
3. Create `~/.local/share/nautilus-separators/` for separator dummy directories.
4. Install the `nautilus-separator` CLI tool into `~/.local/bin/`.
5. Restart Nautilus via `nautilus -q` to activate the extension.

---

## Usage

### Using the CLI (`nautilus-separator`)

The included command-line tool makes managing sidebar sections effortless:

#### 1. Add a separator header
```bash
nautilus-separator add "WORK"
nautilus-separator add "PROJECTS"
nautilus-separator add "PERSONAL"
```

#### 2. List all configured separators
```bash
nautilus-separator list
```
*Output:*
```text
Configured Nautilus Sidebar Separators:
────────────────────────────────────────────────────────────────────
#    NAME                   SLUG               STATUS      
────────────────────────────────────────────────────────────────────
1    WORK                   work               ✔ valid     
2    PROJECTS               projects           ✔ valid     
3    PERSONAL               personal           ✔ valid     
────────────────────────────────────────────────────────────────────
Total: 3 separator(s). You can drag them directly inside Nautilus sidebar.
```

#### 3. Remove a separator
```bash
nautilus-separator remove "WORK"
# or remove by slug:
nautilus-separator remove work
```

#### 4. Clean all separators
```bash
nautilus-separator clean
```

#### 5. Restart Nautilus
```bash
nautilus-separator restart
```

---

### Drag & Drop in Nautilus

Once added:
1. Open **Files (Nautilus)**.
2. Grab any separator by clicking and dragging it up or down in the Bookmarks sidebar.
3. Drag your favorite folders beneath their respective headers to create distinct groups.

---

### Manual Configuration (Without CLI)

Separators are stored in the standard GTK bookmarks file (`~/.config/gtk-3.0/bookmarks`).

Each separator requires:
1. A unique empty folder (e.g. `mkdir -p ~/.local/share/nautilus-separators/my-section`)
2. An entry in `~/.config/gtk-3.0/bookmarks` formatted as:
   ```text
   file:///home/<username>/.local/share/nautilus-separators/my-section # MY SECTION
   ```
3. Restart Nautilus: `nautilus -q`.

---

## Technical Architecture: The "Trojan Bookmark"

GNOME Files does not expose an official public API for extensions to inject custom top-level categories or separators directly into the sidebar tree. To achieve seamless, native drag-and-drop reordering without patching Nautilus, `nautilus-sidebar-separators` utilizes the **Trojan Bookmark** pattern:

```
[ GTK Bookmarks (~/.config/gtk-3.0/bookmarks) ]
           │
           ▼
[ file://.../nautilus-separators/<slug> # TITLE ]  <── Distinct URI per separator
           │
           ▼
[ Nautilus Sidebar GTK4 ListBox ]
  └─ GtkListBoxRow
       └─ GtkBox
            ├─ GtkImage (Folder Icon)       ──> Hidden via extension (set_visible(False))
            ├─ GtkLabel ("# TITLE")         ──> Stripped to "TITLE", uppercase styled, no ellipsize
            └─ GtkSeparator (New!)          ──> Injected dynamically with hexpand=True
```

### 1. Circumventing URI Deduplication
GTK's bookmark manager automatically consolidates bookmarks sharing the same URI into a single row. Pointing all separators to a single dummy directory (like `/tmp`) causes multiple separators to collapse. To prevent this, each separator is mapped to a dedicated placeholder directory in `~/.local/share/nautilus-separators/<slug>`.

### 2. GTK4 Widget Tree Scanning
Running inside the Nautilus process via `nautilus-python`, the extension sets up a periodic main-loop timer (`GLib.timeout_add(300, ...)`). The scanner:
- Recursively walks all open windows and child widgets.
- Discovers `Gtk.Label` instances matching the `# ` prefix.
- Walks up the widget hierarchy to find the enclosing `Gtk.ListBoxRow`.

### 3. Row Transformation
When a separator bookmark row is encountered:
- **`Gtk.ListBoxRow`**: `set_selectable(False)` and `set_activatable(False)` are invoked. This prevents users from selecting or navigating into the placeholder directory while preserving GTK's native drag source for reordering.
- **Folder Icon**: Scans the row for `Gtk.Image` and sets `set_visible(False)`.
- **Label**: Cleans the prefix (`# WORK` becomes `WORK`), disables text ellipsizing (`Pango.EllipsizeMode.NONE`, `max_width_chars = -1`), and applies uppercase subheader typography.
- **Divider Line**: Instantiates a horizontal `Gtk.Separator` with `hexpand=True`, `valign=Gtk.Align.CENTER`, and appends it to the container box to dynamically stretch across the remaining row width.

### 4. GNOME / Python 3.14 Introspection Safety
Recent versions of GNOME and Python 3.14 pre-load the Nautilus introspection namespace (`Nautilus 4.1` or `4.0`). Calling `gi.require_version('Nautilus', ...)` in Python extensions causes an immediate crash:
```
ValueError: Namespace Nautilus is already loaded with version 4.1
```
The extension safely declares **only** `gi.require_version('Gtk', '4.0')`, guaranteeing full forward and backward compatibility across GNOME 43 through 49+.

---

## Uninstallation

To completely remove the extension, CLI utility, dummy folders, and separator bookmarks:

```bash
./uninstall.sh
```

Or manually:
```bash
rm -f ~/.local/share/nautilus-python/extensions/sidebar_separators.py
rm -f ~/.local/bin/nautilus-separator
rm -rf ~/.local/share/nautilus-separators
# Remove lines containing 'nautilus-separators' or '# ' from ~/.config/gtk-3.0/bookmarks
nautilus -q
```

---

## Contributing

Contributions, bug reports, and suggestions are warmly welcome!
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Run the unit tests (`python3 -m unittest discover -s tests`).
4. Commit your changes and open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE).
