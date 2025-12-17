"""
File management utilities for saving and loading keybinds.
"""
import json
import os
from tkinter import messagebox


def save_binds(config_file, binds, auto_enter):
    """Save keybinds to JSON file."""
    try:
        # Ensure parent directory exists
        cfg_dir = os.path.dirname(config_file)
        if cfg_dir:
            os.makedirs(cfg_dir, exist_ok=True)

        # Debug: log what we're about to save
        try:
            print(f"[Keybind] Saving to {config_file} -> {len(binds)} macro(s), auto_enter={auto_enter}")
        except Exception:
            pass

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'binds': binds,
                'auto_enter': auto_enter
            }, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        # Also print the error to the terminal to help debugging.
        try:
            print(f"[Keybind] Save error: {e}")
        except Exception:
            pass

        messagebox.showerror(
            "Save Error",
            "Gagal menyimpan keybinds.json\n\n"
            f"Path: {config_file}\n"
            f"Error: {e}"
        )
        return False


def load_binds(config_file, legacy_config_file=None):
    """Load keybinds from JSON file. Returns (binds, auto_enter, migrated)."""
    load_path = config_file
    migrated = False

    if not os.path.exists(load_path):
        if legacy_config_file and os.path.exists(legacy_config_file):
            load_path = legacy_config_file
            migrated = True
        else:
            return {}, False, False

    try:
        # Read raw content first so we can gracefully handle empty / invalid JSON.
        with open(load_path, 'r', encoding='utf-8') as f:
            raw = f.read().strip()

        if not raw:
            # Empty file → treat as fresh install.
            data = {"binds": {}, "auto_enter": False}
        else:
            data = json.loads(raw)

        binds = data.get('binds', {})
        auto_enter = data.get('auto_enter', False)

        # Support old format (string) and new format (dict)
        for key, bind_data in binds.items():
            if isinstance(bind_data, str):
                text = bind_data
                binds[key] = {"label": f"Macro {key}", "text": text}

        return binds, auto_enter, migrated

    except json.JSONDecodeError:
        # Corrupted JSON → return empty
        messagebox.showwarning(
            "Reset keybinds.json",
            "File keybinds.json rusak / tidak valid.\n\n"
            "File telah di-reset ke kondisi kosong (tanpa macro)."
        )
        return {}, False, False
    except Exception as e:
        messagebox.showerror(
            "Load Error",
            "Gagal load keybinds.json\n\n"
            f"Path: {config_file}\n"
            f"Error: {e}"
        )
        return {}, False, False

