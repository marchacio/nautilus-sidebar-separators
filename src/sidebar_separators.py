#!/usr/bin/env python3
"""
Nautilus Sidebar Separators Extension
====================================
Transforms special bookmarks (prefixed with '# ') in GNOME Files (Nautilus 43+)
sidebar into clean, customizable, draggable category headers with horizontal dividers.

Part of the nautilus-sidebar-separators project:
https://github.com/m4rco-m/nautilus-sidebar-separators
"""

import sys
import gi

# CRITICAL COMPATIBILITY NOTE:
# Explicitly require Gtk 4.0 only.
# Do NOT call gi.require_version('Nautilus', ...) here: Nautilus already pre-loads
# its own introspection namespace (version 4.1 or 4.0 depending on the GNOME version),
# and calling require_version with a mismatch raises:
# ValueError: Namespace Nautilus is already loaded with version 4.1
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, GLib, GObject, Pango, Nautilus  # noqa: E402


class SidebarSeparatorsExtension(GObject.GObject, Nautilus.MenuProvider):
    """
    Nautilus Python extension that monitors GTK4 sidebar widgets and formats
    Trojan bookmarks into elegant sidebar section headers and separators.
    """

    SEPARATOR_PREFIX = "# "
    CSS_CLASS_ROW = "nautilus-sidebar-separator-row"
    CSS_CLASS_LABEL = "nautilus-sidebar-separator-label"
    CSS_CLASS_LINE = "nautilus-sidebar-separator-line"
    MARKER_WIDGET_NAME = "nautilus-sidebar-separator-processed"

    CUSTOM_CSS = b"""
    .nautilus-sidebar-separator-row {
        margin-top: 4px;
        margin-bottom: 0px;
        padding-top: 0px;
        padding-bottom: 0px;
        min-height: 18px;
        background: transparent;
        opacity: 0.90;
    }

    .nautilus-sidebar-separator-row:hover {
        background: transparent;
    }

    .nautilus-sidebar-separator-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: alpha(currentColor, 0.55);
        margin-left: 0px;
        margin-start: 0px;
        padding-left: 0px;
        padding-start: 0px;
        margin-right: 8px;
    }

    .nautilus-sidebar-separator-line {
        min-height: 1px;
        opacity: 0.25;
        margin-top: 0px;
        margin-bottom: 0px;
    }
    """

    def __init__(self):
        super().__init__()
        self._css_initialized = False
        self._init_css()

        # Start periodic scanning of GTK4 widget tree for sidebar bookmarks
        # 300ms interval provides instantaneous UI reaction with negligible CPU usage.
        GLib.timeout_add(300, self._on_scan_timer)

    def _init_css(self):
        """Registers custom CSS rules into GTK4 default display style context."""
        if self._css_initialized:
            return

        try:
            display = Gdk.Display.get_default()
            if display is not None:
                provider = Gtk.CssProvider()
                provider.load_from_data(self.CUSTOM_CSS)
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
                self._css_initialized = True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # Non-fatal: extension will still function with fallback styles
            print(f"[nautilus-sidebar-separators] CSS init warning: {exc}", file=sys.stderr)

    def _on_scan_timer(self) -> bool:
        """Periodic callback running in GLib main loop to process open windows."""
        if not self._css_initialized:
            self._init_css()

        try:
            # GTK 4: inspect all toplevel windows
            toplevels = Gtk.Window.get_toplevels()
            n_items = toplevels.get_n_items() if hasattr(toplevels, "get_n_items") else 0
            for i in range(n_items):
                window = toplevels.get_item(i)
                if isinstance(window, Gtk.Window):
                    self._scan_widget_tree(window)

            # Fallback for Gtk.Application windows if available
            app = Gtk.Application.get_default()
            if app is not None and hasattr(app, "get_windows"):
                for window in app.get_windows():
                    self._scan_widget_tree(window)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"[nautilus-sidebar-separators] Scan error: {exc}", file=sys.stderr)

        # Return True to ensure GLib keeps repeating the timeout
        return True

    def _scan_widget_tree(self, root: Gtk.Widget):
        """Recursively walks GTK4 widget hierarchy to detect separator bookmark labels."""
        child = root.get_first_child()
        while child is not None:
            if isinstance(child, Gtk.Label):
                self._inspect_label(child)
            else:
                self._scan_widget_tree(child)
            child = child.get_next_sibling()

    def _inspect_label(self, label: Gtk.Label):
        """Checks if a Gtk.Label represents a separator bookmark and styles it."""
        text = label.get_text() or ""
        widget_name = label.get_name() or ""

        is_raw_separator = text.startswith(self.SEPARATOR_PREFIX) or text.startswith("#")
        is_processed_separator = widget_name == self.MARKER_WIDGET_NAME

        if not (is_raw_separator or is_processed_separator):
            return

        # Find enclosing Gtk.ListBoxRow in sidebar
        row = self._find_ancestor_list_box_row(label)
        if row is None:
            return

        # 1. Disable row selection, activation and focus
        row.set_selectable(False)
        row.set_activatable(False)
        row.set_can_focus(False)
        row.set_margin_top(4)
        row.set_margin_bottom(0)
        if not row.has_css_class(self.CSS_CLASS_ROW):
            row.add_css_class(self.CSS_CLASS_ROW)

        # 2. Reconfigure Gtk.Label: reset ellipsizing, expand, margins and alignment
        label.set_ellipsize(Pango.EllipsizeMode.NONE)
        label.set_max_width_chars(-1)
        label.set_hexpand(False)
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(0)
        label.set_margin_top(0)
        label.set_margin_bottom(0)
        if not label.has_css_class(self.CSS_CLASS_LABEL):
            label.add_css_class(self.CSS_CLASS_LABEL)

        # Clean display text (strip leading '# ' or '#')
        if is_raw_separator:
            if text.startswith(self.SEPARATOR_PREFIX):
                clean_title = text[len(self.SEPARATOR_PREFIX):].strip()
            else:
                clean_title = text.lstrip("#").strip()

            label.set_text(clean_title)
            label.set_name(self.MARKER_WIDGET_NAME)

        # 3. Hide folder icon inside this row
        self._hide_images(row)

        # 4. Insert horizontal Gtk.Separator into the parent box container
        parent_container = label.get_parent()
        if parent_container is not None:
            self._ensure_separator_line(parent_container)

    def _find_ancestor_list_box_row(self, widget: Gtk.Widget) -> Gtk.ListBoxRow | None:
        """Finds closest Gtk.ListBoxRow ancestor."""
        current = widget.get_parent()
        while current is not None:
            if isinstance(current, Gtk.ListBoxRow):
                return current
            current = current.get_parent()
        return None

    def _hide_images(self, root: Gtk.Widget):
        """Hides any Gtk.Image (folder icon) within the widget subtree."""
        child = root.get_first_child()
        while child is not None:
            if isinstance(child, Gtk.Image):
                child.set_visible(False)
            else:
                self._hide_images(child)
            child = child.get_next_sibling()

    def _ensure_separator_line(self, container: Gtk.Widget):
        """Ensures a horizontal Gtk.Separator with hexpand exists in container."""
        # Check if separator already exists
        child = container.get_first_child()
        while child is not None:
            if isinstance(child, Gtk.Separator) and child.has_css_class(self.CSS_CLASS_LINE):
                return
            child = child.get_next_sibling()

        # Create and append separator
        separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        separator.set_hexpand(True)
        separator.set_valign(Gtk.Align.CENTER)
        separator.set_margin_top(0)
        separator.set_margin_bottom(0)
        separator.add_css_class(self.CSS_CLASS_LINE)

        if hasattr(container, "append"):
            container.append(separator)

    # Nautilus MenuProvider interface stubs (required by nautilus-python loader)
    def get_file_items(self, *args):  # pylint: disable=unused-argument
        return []

    def get_background_items(self, *args):  # pylint: disable=unused-argument
        return []
