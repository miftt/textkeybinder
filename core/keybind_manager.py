"""
Main Keybind Manager class that coordinates all components.
"""
import tkinter as tk
from tkinter import messagebox
import keyboard
import threading

from config import (
    APP_TITLE,
    APP_TITLE_FALLBACK,
    WINDOW_SIZE,
    MIN_WINDOW_SIZE,
    AVAILABLE_HOTKEYS,
    COLORS,
    TYPING_DELAY_PER_CHAR,
)
from core.typing_manager import TypingManager
from utils.file_manager import save_binds, load_binds
from config import get_config_path, get_legacy_config_path

# Try to import ttkbootstrap for modern UI
try:
    import ttkbootstrap as ttkb
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    ttkb = None


class ModernKeybindManager:
    """Main application class for managing text macros with hotkeys."""
    
    def __init__(self):
        # Initialize window
        if TTKBOOTSTRAP_AVAILABLE:
            self.root = ttkb.Window(themename="darkly")
            self.root.title(APP_TITLE)
            self.use_ttkbootstrap = True
        else:
            self.root = tk.Tk()
            self.root.title(APP_TITLE_FALLBACK)
            self.use_ttkbootstrap = False
        
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)
        
        if not self.use_ttkbootstrap:
            self.root.configure(bg=COLORS["bg_main"])
        
        # Application state
        self.binds = {}
        self.is_paused = False
        self.selected_macro = None
        self.auto_enter = tk.BooleanVar()

        # Typing speed (detik per karakter) - bisa diatur user
        self.per_char_delay = tk.DoubleVar(value=TYPING_DELAY_PER_CHAR)
        
        # Config paths
        self.legacy_config_file = get_legacy_config_path()
        self.config_file = get_config_path()
        
        try:
            print(f"[Keybind] Using config file: {self.config_file}")
        except Exception:
            pass
        
        # Keyboard shortcut
        self.root.bind("<Control-s>", lambda e: self.save_current_macro())

        # Typing manager (pakai callback ke variable delay)
        self.typing_manager = TypingManager(
            lambda: self.auto_enter.get(),
            per_char_delay_callback=lambda: self.per_char_delay.get(),
        )
        
        # Available hotkeys
        self.available_hotkeys = AVAILABLE_HOTKEYS
        
        # Setup UI (will be imported from ui.gui)
        from ui.gui import setup_gui
        setup_gui(self)
        
        # Set default hotkey to F1
        self.key_entry.set('F1')
        
        # Load saved binds
        self.load_binds()

    # ----------------------
    # Helper: hotkey mapping
    # ----------------------
    @staticmethod
    def _normalize_hotkey(key: str) -> str:
        """
        Normalize user-friendly hotkey strings to the format expected by
        the `keyboard` library.

        Example:
        - "numpad 1" -> "num 1"
        - "numpad +" -> "num +"
        """
        if not key:
            return key

        lower = key.lower()
        if lower.startswith("numpad "):
            suffix = key[7:].strip()  # everything after "numpad "
            return f"num {suffix}"
        return key
    
    def save_current_macro(self):
        """Save the current macro being edited."""
        label = self.label_entry.get().strip()
        key = self.key_entry.get().strip()
        text = self.text_editor.get("1.0", tk.END).strip()
        
        if not label:
            messagebox.showwarning("Warning", "Macro Name harus diisi!\n(Biar gampang diinget)")
            self.label_entry.focus()
            return
        
        if not key:
            messagebox.showwarning("Warning", "Hotkey harus diisi!\n(Contoh: F1, ., ctrl+a)")
            self.key_entry.focus()
            return
        
        if not text:
            messagebox.showwarning("Warning", "Text content harus diisi!")
            self.text_editor.focus()
            return

        old_key = self.selected_macro
        key_changed = bool(old_key) and old_key != key

        # Update in-memory first (gunakan key seperti yang user lihat)
        self.binds[key] = {
            "label": label,
            "text": text
        }

        hotkey_registered = False
        hotkey_error = None

        # Register hotkey
        try:
            norm_key = self._normalize_hotkey(key)
            try:
                keyboard.remove_hotkey(norm_key)
            except Exception:
                pass

            keyboard.add_hotkey(
                norm_key,
                lambda t=text: self.typing_manager.send_text(t),
                suppress=True,
                trigger_on_release=True,
            )
            hotkey_registered = True
        except Exception as e:
            hotkey_error = e

        # Remove old key if new one registered successfully
        if key_changed and hotkey_registered:
            norm_old = self._normalize_hotkey(old_key)
            try:
                keyboard.remove_hotkey(norm_old)
            except Exception:
                pass
            if old_key in self.binds:
                del self.binds[old_key]

        # Persist
        self.selected_macro = key
        self.refresh_macro_list()
        self.save_binds()
        self.update_status()

        if hotkey_registered:
            messagebox.showinfo("Success", f"✓ Macro '{label}' berhasil disimpan!\nHotkey: {key}")
        else:
            messagebox.showwarning(
                "Saved (Hotkey Not Active)",
                f"✓ Macro '{label}' berhasil disimpan ke file.\n\n"
                f"Tapi hotkey '{key}' gagal diregister, jadi belum bisa dipakai.\n\n"
                f"Error: {hotkey_error}\n\n"
                "Coba jalankan sebagai Administrator, atau pakai format key seperti:\n"
                "F1, F2, ., ctrl+a, shift+f1"
            )
    
    def delete_current_macro(self):
        """Delete the currently selected macro."""
        key = self.key_entry.get().strip()
        
        if not key:
            messagebox.showwarning("Warning", "Tidak ada macro yang dipilih!")
            return
        
        if key not in self.binds:
            messagebox.showwarning("Warning", "Macro tidak ditemukan!\nPilih dari list di sebelah kiri.")
            return
        
        label = self.binds[key].get("label", key)
        
        if messagebox.askyesno("Confirm Delete", f"Yakin ingin hapus macro:\n\n'{label}' (Hotkey: {key})?"):
            try:
                keyboard.remove_hotkey(self._normalize_hotkey(key))
            except:
                pass
            
            del self.binds[key]
            self.refresh_macro_list()
            self.save_binds()
            self.add_new_macro()
            self.update_status()
            messagebox.showinfo("Deleted", f"✓ Macro '{label}' berhasil dihapus!")
    
    def toggle_pause(self):
        """Toggle pause/play state of all hotkeys."""
        self.is_paused = not self.is_paused
        self.typing_manager.is_paused = self.is_paused
        
        if self.is_paused:
            keyboard.unhook_all()
            self.update_status()
            try:
                if self.use_ttkbootstrap:
                    self.pause_button.config(text="▶ Play", bootstyle="success")
                else:
                    self.pause_button.config(text="▶ Play", bg=COLORS["accent_teal"], 
                                            activebackground=COLORS["accent_teal_dark"])
            except Exception:
                pass
            messagebox.showinfo("Paused", "⏸ Semua hotkey dinonaktifkan sementara.")
        else:
            for key, data in self.binds.items():
                norm_key = self._normalize_hotkey(key)
                try:
                    keyboard.add_hotkey(
                        norm_key,
                        lambda t=data["text"]: self.typing_manager.send_text(t),
                        suppress=True,
                        trigger_on_release=True,
                    )
                except Exception:
                    pass
            self.update_status()
            try:
                if self.use_ttkbootstrap:
                    self.pause_button.config(text="⏸ Pause", bootstyle="warning")
                else:
                    self.pause_button.config(text="⏸ Pause", bg=COLORS["accent_orange"],
                                            activebackground=COLORS["accent_orange_dark"])
            except Exception:
                pass
            messagebox.showinfo("Resumed", "▶ Hotkey aktif kembali!")
    
    def save_binds(self):
        """Save binds to file."""
        save_binds(self.config_file, self.binds, self.auto_enter.get())
    
    def load_binds(self):
        """Load binds from file."""
        binds, auto_enter, migrated = load_binds(self.config_file, self.legacy_config_file)
        
        if not binds and not migrated:
            return
        
        self.binds = binds
        self.auto_enter.set(auto_enter)

        # Register hotkeys
        for key, bind_data in self.binds.items():
            text = bind_data.get("text", "")
            norm_key = self._normalize_hotkey(key)
            try:
                keyboard.add_hotkey(
                    norm_key,
                    lambda t=text: self.typing_manager.send_text(t),
                    suppress=True,
                    trigger_on_release=True,
                )
            except Exception:
                pass

        self.refresh_macro_list()
        self.update_status()

        # If migrated, save to new location
        if migrated:
            self.save_binds()
            self.status_bar.config(
                text=f"✨ Migrated macros to {self.config_file}",
                fg=COLORS["accent_teal"]
            )
    
    def refresh_macro_list(self):
        """Refresh the macro list in the sidebar."""
        from ui.gui import create_macro_item
        for widget in self.macro_frame.winfo_children():
            widget.destroy()
        
        for key, data in self.binds.items():
            create_macro_item(self, key, data)
    
    def select_macro(self, key):
        """Select a macro from the list and load it into the editor."""
        self.selected_macro = key
        data = self.binds[key]
        
        self.label_entry.delete(0, tk.END)
        self.label_entry.insert(0, data.get("label", ""))
        
        # Combobox pakai set() untuk set value
        self.key_entry.set(key)
        
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", data.get("text", ""))
    
    def add_new_macro(self):
        """Clear the editor to add a new macro."""
        self.selected_macro = None
        self.label_entry.delete(0, tk.END)
        self.key_entry.set('F1')  # Set default to F1
        self.text_editor.delete("1.0", tk.END)
        self.label_entry.focus()
    
    def update_status(self):
        """Update status bar text."""
        count = len(self.binds)
        if self.is_paused:
            self.status_bar.config(
                text=f"⏸ Paused • Status: Stopped • {count} macro{'s' if count != 1 else ''} loaded",
                fg=COLORS["accent_orange"],
            )
        else:
            self.status_bar.config(
                text=f"▶ Playing • Status: Playing • {count} macro{'s' if count != 1 else ''} loaded",
                fg=COLORS["accent_teal"],
            )
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

