import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import keyboard
import json
import os
import sys
import threading
import time
import socket

# Try to import ttkbootstrap for modern UI (optional, falls back to regular tkinter if not available)
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    ttkb = None

class ModernKeybindManager:
    def __init__(self):
        # Use ttkbootstrap for modern UI if available, otherwise fallback to regular tkinter
        if TTKBOOTSTRAP_AVAILABLE:
            self.root = ttkb.Window(themename="darkly")  # Modern dark theme with glassmorphism
            self.root.title("✨ TEXT MACRO KEYBINDER BY MIFUZI")
            self.use_ttkbootstrap = True
        else:
            self.root = tk.Tk()
            self.root.title("TEXT MACRO KEYBINDER BY MIFUZI")
            self.use_ttkbootstrap = False
        
        # Default tampilan dibuat kompak tapi tinggi cukup agar semua elemen terlihat.
        self.root.geometry("900x600")
        # Boleh dikecilkan tapi tidak kurang dari 500x600 agar layout tetap rapi.
        self.root.minsize(900, 600)
        
        if not self.use_ttkbootstrap:
            # Modern gradient background (genz style) - fallback
            self.root.configure(bg="#0a0a0f")
        
        self.binds = {}  # Format: {key: {"label": "name", "text": "content"}}
        
        # Prefer a portable save file next to the script/exe (NOT Roaming).
        # We'll still *read* legacy Roaming data once (if present) and migrate it.
        self.legacy_config_file = self._get_legacy_config_path()
        self.config_file = self._get_config_path()
        # Simple debug: print where keybinds.json is actually stored.
        try:
            print(f"[Keybind] Using config file: {self.config_file}")
        except Exception:
            pass

        # Keyboard shortcut supaya tetap bisa save walaupun tombol tidak kelihatan (mis. window kecil).
        self.root.bind("<Control-s>", lambda e: self.save_current_macro())

        self.is_paused = False
        self.auto_enter = tk.BooleanVar()
        self.selected_macro = None
        # Lock untuk prevent multiple simultaneous typing (mencegah double-typing bug).
        self.typing_lock = threading.Lock()
        
        # Daftar hotkey yang bisa dipilih user (scrollable dropdown)
        self.available_hotkeys = [
            # Function Keys
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            # Numpad Numbers
            "numpad 0", "numpad 1", "numpad 2", "numpad 3", "numpad 4",
            "numpad 5", "numpad 6", "numpad 7", "numpad 8", "numpad 9",
            # Numpad Operators
            "numpad +", "numpad -", "numpad *", "numpad /", "numpad enter", "numpad .",
            # Special Characters
            ".", ",", ";", ":", "'", '"', "[", "]", "{", "}", "\\", "|", "/", "?",
            # Modifier Combinations (Function Keys)
            "ctrl+F1", "ctrl+F2", "ctrl+F3", "ctrl+F4", "ctrl+F5",
            "shift+F1", "shift+F2", "shift+F3", "shift+F4", "shift+F5",
            "alt+F1", "alt+F2", "alt+F3", "alt+F4", "alt+F5",
            # Modifier Combinations (Special Keys)
            "ctrl+.", "ctrl+,", "ctrl+;", "ctrl+:", "ctrl+/",
            "shift+.", "shift+,", "shift+;", "shift+:", "shift+/",
            "alt+.", "alt+,", "alt+;", "alt+:", "alt+/",
            # Common Modifier Combinations
            "ctrl+a", "ctrl+b", "ctrl+c", "ctrl+d", "ctrl+e", "ctrl+f", "ctrl+g", "ctrl+h",
            "ctrl+i", "ctrl+j", "ctrl+k", "ctrl+l", "ctrl+m", "ctrl+n", "ctrl+o", "ctrl+p",
            "ctrl+q", "ctrl+r", "ctrl+s", "ctrl+t", "ctrl+u", "ctrl+v", "ctrl+w", "ctrl+x",
            "ctrl+y", "ctrl+z",
            "shift+a", "shift+b", "shift+c", "shift+d", "shift+e", "shift+f", "shift+g",
            "alt+a", "alt+b", "alt+c", "alt+d", "alt+e", "alt+f", "alt+g",
        ]
        
        self.setup_gui()
        self.load_binds()
        
    def _can_write_file(self, path):
        """Best-effort check if we can create/append a file at `path`."""
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "a", encoding="utf-8"):
                pass
            return True
        except Exception:
            return False

    def _get_legacy_config_path(self):
        """Old location (Roaming). We only use this to migrate existing users."""
        try:
            appdata = os.getenv("APPDATA")
            if not appdata:
                return None
            return os.path.join(appdata, "SAMP_Keybind", "keybinds.json")
        except Exception:
            return None

    def _get_config_path(self):
        r"""Return a stable path for keybinds.json.
        Prefer a *portable* keybinds.json next to the running script/executable.
        If that folder is not writable, fallback to Documents (NOT Roaming).
        """
        # Portable: directory of the running script/executable
        try:
            base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()

        portable_path = os.path.join(base_dir, "keybinds.json")
        if self._can_write_file(portable_path):
            return portable_path

        # Fallback: Documents\SAMP_Keybind\keybinds.json
        try:
            home = os.path.expanduser("~")
            documents = os.path.join(home, "Documents")
            root_dir = documents if os.path.isdir(documents) else home
            return os.path.join(root_dir, "SAMP_Keybind", "keybinds.json")
        except Exception:
            return os.path.join(os.getcwd(), "keybinds.json")
    def setup_gui(self):
        # Main container dengan gradient background effect (glassmorphism base)
        main_container = tk.Frame(self.root, bg="#0a0a0f")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDEBAR - Macro List dengan glassmorphism effect
        left_frame = tk.Frame(main_container, bg="#1a1a2e", width=260)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=12, pady=12)
        left_frame.pack_propagate(False)
        
        # Sidebar Header dengan gradient effect (modern genz style)
        header = tk.Frame(left_frame, bg="#16213e", height=55)
        header.pack(fill=tk.X, padx=0, pady=0)
        tk.Label(header, text="✨ TEXT MACROS", font=("Segoe UI", 13, "bold"), 
                bg="#16213e", fg="#ffffff").pack(pady=15)
        
        # Macro List Container with Scrollbar (glass effect)
        list_container = tk.Frame(left_frame, bg="#1a1a2e")
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.macro_canvas = tk.Canvas(list_container, bg="#1a1a2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.macro_canvas.yview,
                                 bg="#2a2a3e", troughcolor="#1a1a2e", activebackground="#3a3a4e",
                                 width=10, borderwidth=0)
        self.macro_frame = tk.Frame(self.macro_canvas, bg="#1a1a2e")
        
        self.macro_frame.bind("<Configure>", lambda e: self.macro_canvas.configure(scrollregion=self.macro_canvas.bbox("all")))
        self.macro_canvas.create_window((0, 0), window=self.macro_frame, anchor="nw")
        self.macro_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.macro_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add New Macro Button (modern glassmorphism button)
        btn_frame = tk.Frame(left_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, padx=8, pady=8)
        
        if self.use_ttkbootstrap:
            # Use ttkbootstrap modern button with glassmorphism
            add_btn = ttkb.Button(btn_frame, text="✨ + Add New Macro", command=self.add_new_macro,
                                 bootstyle="success", width=20)
            add_btn.pack(fill=tk.X, pady=2)
        else:
            # Fallback to regular button
            add_btn = tk.Button(btn_frame, text="✨ + Add New Macro", command=self.add_new_macro,
                     bg="#00d4aa", fg="white", font=("Segoe UI", 11, "bold"),
                     relief=tk.FLAT, cursor="hand2", pady=12, activebackground="#00b894",
                     activeforeground="white", bd=0)
            add_btn.pack(fill=tk.X)
            # Hover effect
            def add_btn_enter(e): add_btn.config(bg="#00b894")
            def add_btn_leave(e): add_btn.config(bg="#00d4aa")
            add_btn.bind("<Enter>", add_btn_enter)
            add_btn.bind("<Leave>", add_btn_leave)
        
        # RIGHT PANEL - Editor dengan glassmorphism effect
        right_frame = tk.Frame(main_container, bg="#1a1a2e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        right_canvas = tk.Canvas(right_frame, bg="#1a1a2e", highlightthickness=0)
        right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview,
                                      bg="#2a2a3e", troughcolor="#1a1a2e", activebackground="#3a3a4e",
                                      width=10, borderwidth=0)

        right_inner = tk.Frame(right_canvas, bg="#1a1a2e")
        right_inner.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        right_canvas.create_window((0, 0), window=right_inner, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Editor Header (modern glassmorphism style)
        editor_header = tk.Frame(right_inner, bg="#16213e", height=50)
        editor_header.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        tk.Label(editor_header, text="🎨 TEXT MACRO EDITOR", font=("Segoe UI", 16, "bold"),
                bg="#16213e", fg="#ffffff").pack(anchor="w", padx=20, pady=15)
        
        # Label/Name Input (glassmorphism card)
        label_frame = tk.Frame(right_inner, bg="#16213e")
        label_frame.pack(fill=tk.X, padx=16, pady=8)
        
        tk.Label(label_frame, text="Macro Name", font=("Segoe UI", 10, "bold"),
                bg="#16213e", fg="#b8b8d1").pack(anchor="w", pady=(0, 6))
        
        self.label_entry = tk.Entry(label_frame, font=("Segoe UI", 11), bg="#0f3460",
                                    fg="#ffffff", insertbackground="#00d4aa", relief=tk.FLAT,
                                    highlightthickness=2, highlightbackground="#00d4aa",
                                    highlightcolor="#00d4aa", bd=0)
        self.label_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
        
        tk.Label(label_frame, text="💡 Contoh: Mute Command, Welcome Message", 
                font=("Segoe UI", 8), bg="#16213e", fg="#6c6c8a").pack(anchor="w")
        
        # Key Input (Dropdown/Combobox) - glassmorphism style
        key_frame = tk.Frame(right_inner, bg="#16213e")
        key_frame.pack(fill=tk.X, padx=16, pady=8)
        
        tk.Label(key_frame, text="Hotkey", font=("Segoe UI", 10, "bold"),
                bg="#16213e", fg="#b8b8d1").pack(anchor="w", pady=(0, 6))
        
        # Style untuk Combobox dengan glassmorphism effect
        if self.use_ttkbootstrap:
            # Use ttkbootstrap modern combobox
            self.key_entry = ttkb.Combobox(key_frame, 
                                          values=self.available_hotkeys,
                                          font=("Segoe UI", 11),
                                          bootstyle="dark",
                                          state="readonly",
                                          height=15)
            self.key_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
        else:
            # Fallback to regular ttk combobox with custom styling
            style = ttk.Style()
            style.theme_use('clam')
            style.configure("Glass.TCombobox",
                           fieldbackground="#0f3460",
                           background="#0f3460",
                           foreground="#ffffff",
                           borderwidth=2,
                           relief="flat",
                           arrowcolor="#00d4aa",
                           darkcolor="#0f3460",
                           lightcolor="#0f3460",
                           bordercolor="#00d4aa")
            style.map("Glass.TCombobox",
                     fieldbackground=[("readonly", "#0f3460"), ("active", "#0f3460")],
                     background=[("readonly", "#0f3460"), ("active", "#0f3460")],
                     foreground=[("readonly", "#ffffff"), ("active", "#ffffff")],
                     arrowcolor=[("readonly", "#00d4aa"), ("active", "#00d4aa")],
                     bordercolor=[("readonly", "#00d4aa"), ("active", "#00d4aa")],
                     darkcolor=[("readonly", "#0f3460"), ("active", "#0f3460")],
                     lightcolor=[("readonly", "#0f3460"), ("active", "#0f3460")])
            
            self.key_entry = ttk.Combobox(key_frame, 
                                          values=self.available_hotkeys,
                                          font=("Segoe UI", 11),
                                          style="Glass.TCombobox",
                                          state="readonly",
                                          height=15)
            self.key_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
        
        tk.Label(key_frame, text="💡 Klik dropdown untuk pilih hotkey (scrollable)", 
                font=("Segoe UI", 8), bg="#16213e", fg="#6c6c8a").pack(anchor="w")
        
        # Text Content - glassmorphism card
        text_frame = tk.Frame(right_inner, bg="#16213e")
        text_frame.pack(fill=tk.BOTH, expand=False, padx=16, pady=8)
        
        tk.Label(text_frame, text="Text Content", font=("Segoe UI", 10, "bold"),
                bg="#16213e", fg="#b8b8d1").pack(anchor="w", pady=(0, 6))
        
        self.text_editor = scrolledtext.ScrolledText(
            text_frame, font=("Consolas", 10), bg="#0f3460", fg="#ffffff",
            insertbackground="#00d4aa", relief=tk.FLAT, wrap=tk.WORD,
            highlightthickness=2, highlightbackground="#00d4aa",
            highlightcolor="#00d4aa", height=8, bd=0,
            selectbackground="#00d4aa", selectforeground="#0a0a0f"
        )
        self.text_editor.pack(fill=tk.BOTH, expand=False, pady=(0, 4), ipadx=12, ipady=8)
        
        # Options - glassmorphism style
        options_frame = tk.Frame(right_inner, bg="#16213e")
        options_frame.pack(fill=tk.X, padx=16, pady=8)
        
        auto_check = tk.Checkbutton(options_frame, text="✨ Auto Enter (press Enter after text)",
                                   variable=self.auto_enter, font=("Segoe UI", 10),
                                   bg="#16213e", fg="#b8b8d1", selectcolor="#00d4aa",
                                   activebackground="#16213e", activeforeground="#00d4aa",
                                   highlightbackground="#16213e")
        auto_check.pack(anchor="w")
        
        # Action Buttons - modern glassmorphism buttons
        action_frame = tk.Frame(right_inner, bg="#16213e")
        action_frame.pack(fill=tk.X, padx=16, pady=(12, 16))
        
        if self.use_ttkbootstrap:
            # Use ttkbootstrap modern buttons
            save_btn = ttkb.Button(action_frame, text="💾 Save Macro", command=self.save_current_macro,
                         bootstyle="success", width=20)
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            delete_btn = ttkb.Button(action_frame, text="🗑 Delete", command=self.delete_current_macro,
                         bootstyle="danger", width=18)
            delete_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Pause button with dynamic style
            self.pause_button = ttkb.Button(
                action_frame,
                text="⏸ Pause",
                command=self.toggle_pause,
                bootstyle="warning",
                width=20
            )
            self.pause_button.pack(side=tk.LEFT)
        else:
            # Fallback to regular buttons
            save_btn = tk.Button(action_frame, text="💾 Save Macro", command=self.save_current_macro,
                     bg="#00d4aa", fg="white", font=("Segoe UI", 11, "bold"),
                     relief=tk.FLAT, cursor="hand2", width=18, pady=12, bd=0,
                     activebackground="#00b894", activeforeground="white")
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            def save_btn_enter(e): save_btn.config(bg="#00b894")
            def save_btn_leave(e): save_btn.config(bg="#00d4aa")
            save_btn.bind("<Enter>", save_btn_enter)
            save_btn.bind("<Leave>", save_btn_leave)
            
            delete_btn = tk.Button(action_frame, text="🗑 Delete", command=self.delete_current_macro,
                     bg="#ff6b6b", fg="white", font=("Segoe UI", 11, "bold"),
                     relief=tk.FLAT, cursor="hand2", width=15, pady=12, bd=0,
                     activebackground="#ee5a6f", activeforeground="white")
            delete_btn.pack(side=tk.LEFT, padx=(0, 10))
            def delete_btn_enter(e): delete_btn.config(bg="#ee5a6f")
            def delete_btn_leave(e): delete_btn.config(bg="#ff6b6b")
            delete_btn.bind("<Enter>", delete_btn_enter)
            delete_btn.bind("<Leave>", delete_btn_leave)
            
            # Simpan reference ke tombol pause supaya bisa ganti teks/warna sesuai status.
            self.pause_button = tk.Button(
                action_frame,
                text="⏸ Pause",
                command=self.toggle_pause,
                bg="#ffa726",
                fg="white",
                font=("Segoe UI", 11, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                width=18,
                pady=12,
                bd=0,
                activebackground="#fb8c00",
                activeforeground="white"
            )
            self.pause_button.pack(side=tk.LEFT)
            def pause_btn_enter(e): 
                if not self.is_paused:
                    self.pause_button.config(bg="#fb8c00")
            def pause_btn_leave(e): 
                if not self.is_paused:
                    self.pause_button.config(bg="#ffa726")
            self.pause_button.bind("<Enter>", pause_btn_enter)
            self.pause_button.bind("<Leave>", pause_btn_leave)
        
        # Status Bar - modern glassmorphism style
        self.status_bar = tk.Label(self.root, text="✨ Ready • Status: Playing • 0 macros loaded",
                                   font=("Segoe UI", 10), bg="#16213e", fg="#00d4aa",
                                   anchor="w", padx=20, pady=12)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_macro_item(self, key, data):
        # Glassmorphism card style
        item = tk.Frame(self.macro_frame, bg="#16213e", cursor="hand2", relief=tk.FLAT, bd=0)
        item.pack(fill=tk.X, pady=6, padx=4)
        
        # Icon dengan modern style
        icon_label = tk.Label(item, text="⌨", font=("Segoe UI", 16),
                             bg="#16213e", fg="#00d4aa", width=2)
        icon_label.pack(side=tk.LEFT, padx=(12, 12), pady=12)
        
        # Content dengan glassmorphism
        content_frame = tk.Frame(item, bg="#16213e")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(0, 10))
        
        # Label/Name (nama macro yang kamu isi di kanan)
        label = data.get("label", "Unnamed Macro")
        title = tk.Label(
            content_frame,
            text=f"Name: {label}",
            font=("Segoe UI", 11, "bold"),
            bg="#16213e",
            fg="#ffffff",
            anchor="w",
        )
        title.pack(fill=tk.X, pady=(0, 2))
        
        # Hotkey (tombol pemicu, mis: ., F1, ctrl+a)
        hotkey_label = tk.Label(
            content_frame,
            text=f"Hotkey: {key}",
            font=("Segoe UI", 9),
            bg="#16213e",
            fg="#00d4aa",
            anchor="w",
        )
        hotkey_label.pack(fill=tk.X, pady=(0, 2))
        
        # Preview isi Text Content (potongan depan saja)
        text = data.get("text", "")
        preview = text[:45] + "..." if len(text) > 45 else text
        subtitle = tk.Label(
            content_frame,
            text=f"Text: {preview}",
            font=("Segoe UI", 8),
            bg="#16213e",
            fg="#b8b8d1",
            anchor="w",
        )
        subtitle.pack(fill=tk.X)
        
        # Bind click event
        for widget in [item, icon_label, content_frame, title, hotkey_label, subtitle]:
            widget.bind("<Button-1>", lambda e, k=key: self.select_macro(k))
            widget.bind("<Enter>", lambda e, widgets=[item, icon_label, content_frame, title, hotkey_label, subtitle]: self.hover_in(widgets))
            widget.bind("<Leave>", lambda e, widgets=[item, icon_label, content_frame, title, hotkey_label, subtitle]: self.hover_out(widgets))
        
        return item
    
    def hover_in(self, widgets):
        # Modern hover effect dengan glassmorphism
        for w in widgets:
            try:
                if isinstance(w, tk.Frame):
                    w.config(bg="#0f3460")
                elif isinstance(w, tk.Label):
                    current_bg = w.cget("bg")
                    if current_bg == "#16213e":
                        w.config(bg="#0f3460")
                    elif current_bg == "#00d4aa":
                        w.config(bg="#0f3460", fg="#00d4aa")
            except:
                pass
    
    def hover_out(self, widgets):
        # Reset ke original glassmorphism color
        for w in widgets:
            try:
                if isinstance(w, tk.Frame):
                    w.config(bg="#16213e")
                elif isinstance(w, tk.Label):
                    current_text = w.cget("text")
                    if "Name:" in current_text:
                        w.config(bg="#16213e", fg="#ffffff")
                    elif "Hotkey:" in current_text:
                        w.config(bg="#16213e", fg="#00d4aa")
                    elif "Text:" in current_text:
                        w.config(bg="#16213e", fg="#b8b8d1")
                    elif w.cget("text") == "⌨":
                        w.config(bg="#16213e", fg="#00d4aa")
            except:
                pass
    
    def refresh_macro_list(self):
        for widget in self.macro_frame.winfo_children():
            widget.destroy()
        
        for key, data in self.binds.items():
            self.create_macro_item(key, data)
    
    def select_macro(self, key):
        self.selected_macro = key
        data = self.binds[key]
        
        self.label_entry.delete(0, tk.END)
        self.label_entry.insert(0, data.get("label", ""))
        
        # Combobox pakai set() untuk set value
        self.key_entry.set(key)
        
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", data.get("text", ""))
        
    def add_new_macro(self):
        self.selected_macro = None
        self.label_entry.delete(0, tk.END)
        self.key_entry.set('')  # Combobox pakai set() untuk clear
        self.text_editor.delete("1.0", tk.END)
        self.label_entry.focus()
        
    def save_current_macro(self):
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

        # Update (or stage) the bind in-memory first.
        # Important: saving should not depend on hotkey registration succeeding.
        self.binds[key] = {
            "label": label,
            "text": text
        }

        hotkey_registered = False
        hotkey_error = None

        # Register hotkey (non-fatal if it fails).
        try:
            try:
                keyboard.remove_hotkey(key)
            except Exception:
                pass

            # suppress=True → karakter aslinya (mis. ".") tidak ikut tertulis.
            # trigger_on_release=True → lebih stabil di beberapa aplikasi seperti Discord.
            keyboard.add_hotkey(
                key,
                lambda t=text: self.send_text(t),
                suppress=True,
                trigger_on_release=True,
            )
            hotkey_registered = True
        except Exception as e:
            hotkey_error = e

        # Only remove the old macro key if the new hotkey successfully registered.
        # This prevents losing a working macro when the new hotkey string is invalid
        # or keyboard hooks are blocked (e.g., permissions).
        if key_changed and hotkey_registered:
            try:
                keyboard.remove_hotkey(old_key)
            except Exception:
                pass
            if old_key in self.binds:
                del self.binds[old_key]

        # Persist regardless of hotkey registration outcome.
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
                keyboard.remove_hotkey(key)
            except:
                pass
            
            del self.binds[key]
            self.refresh_macro_list()
            self.save_binds()
            self.add_new_macro()
            self.update_status()
            messagebox.showinfo("Deleted", f"✓ Macro '{label}' berhasil dihapus!")
            
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            keyboard.unhook_all()
            # Update tampilan status & tombol
            self.update_status()
            try:
                if self.use_ttkbootstrap:
                    self.pause_button.config(text="▶ Play", bootstyle="success")
                else:
                    self.pause_button.config(text="▶ Play", bg="#00d4aa", activebackground="#00b894")
            except Exception:
                pass
            messagebox.showinfo("Paused", "⏸ Semua hotkey dinonaktifkan sementara.")
        else:
            for key, data in self.binds.items():
                try:
                    keyboard.add_hotkey(
                        key,
                        lambda t=data["text"]: self.send_text(t),
                        suppress=True,
                        trigger_on_release=True,
                    )
                except Exception:
                    pass
            # Update tampilan status & tombol
            self.update_status()
            try:
                if self.use_ttkbootstrap:
                    self.pause_button.config(text="⏸ Pause", bootstyle="warning")
                else:
                    self.pause_button.config(text="⏸ Pause", bg="#ffa726", activebackground="#fb8c00")
            except Exception:
                pass
            messagebox.showinfo("Resumed", "▶ Hotkey aktif kembali!")
            
    def send_text(self, text):
        if self.is_paused:
            return
        if not text:
            return
        # Prevent multiple simultaneous calls (mencegah double-typing bug).
        # Kalau masih ada typing yang jalan, skip yang baru.
        if not self.typing_lock.acquire(blocking=False):
            return
        # Jalankan di thread terpisah supaya tidak nge-freeze GUI.
        threading.Thread(target=self._type_text_with_lock, args=(text,), daemon=True).start()
        
    def _type_text_with_lock(self, text):
        """Wrapper untuk _type_text yang handle lock release."""
        try:
            self._type_text(text)
        finally:
            # Pastikan lock selalu di-release meskipun ada error.
            self.typing_lock.release()
    
    def _type_text(self, text):
        # Delay sebelum mengetik supaya aplikasi tujuan siap menangkap input.
        time.sleep(0.2)
        
        # Pakai metode per karakter dengan delay yang lebih besar dan konsisten
        # untuk memastikan setiap karakter benar-benar terketik, terutama di aplikasi
        # yang berat atau saat RAM tinggi. Delay 0.04-0.05 per karakter cukup untuk
        # mencegah karakter hilang tanpa terlalu lambat.
        try:
            for char in text:
                keyboard.write(char)
                # Delay yang lebih besar untuk memastikan karakter terketik dengan benar
                time.sleep(0.04)
        except Exception as e:
            # Fallback: kalau ada error, coba pakai keyboard.write() langsung
            try:
                keyboard.write(text)
            except Exception:
                pass
        
        # Tambah delay kecil setelah selesai mengetik sebelum tekan Enter (kalau perlu).
        if self.auto_enter.get():
            time.sleep(0.08)
            try:
                keyboard.press_and_release('enter')
            except Exception:
                pass
            
    def save_binds(self):
        try:
            # Ensure parent directory exists (covers fallback paths too)
            cfg_dir = os.path.dirname(self.config_file)
            if cfg_dir:
                os.makedirs(cfg_dir, exist_ok=True)

            # Debug: log what we're about to save
            try:
                print(f"[Keybind] Saving to {self.config_file} -> {len(self.binds)} macro(s), auto_enter={self.auto_enter.get()}")
            except Exception:
                pass

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'binds': self.binds,
                    'auto_enter': self.auto_enter.get()
                }, f, indent=2, ensure_ascii=False)

        except Exception as e:
            # Also print the error to the terminal to help debugging.
            try:
                print(f"[Keybind] Save error: {e}")
            except Exception:
                pass

            messagebox.showerror(
                "Save Error",
                "Gagal menyimpan keybinds.json\n\n"
                f"Path: {self.config_file}\n"
                f"Error: {e}"
            )
            
    def load_binds(self):
        # Load from new portable path; if missing, migrate from legacy Roaming path.
        load_path = self.config_file
        migrated = False

        if not os.path.exists(load_path):
            if self.legacy_config_file and os.path.exists(self.legacy_config_file):
                load_path = self.legacy_config_file
                migrated = True
            else:
                return
        
        try:
            # Read raw content first so we can gracefully handle empty / invalid JSON.
            with open(load_path, 'r', encoding='utf-8') as f:
                raw = f.read().strip()

            if not raw:
                # Empty file → treat as fresh install.
                data = {"binds": {}, "auto_enter": False}
            else:
                data = json.loads(raw)

            self.binds = data.get('binds', {})
            self.auto_enter.set(data.get('auto_enter', False))

            for key, bind_data in self.binds.items():
                # Support old format (string) and new format (dict)
                if isinstance(bind_data, str):
                    text = bind_data
                    self.binds[key] = {"label": f"Macro {key}", "text": text}
                else:
                    text = bind_data.get("text", "")

                try:
                    keyboard.add_hotkey(
                        key,
                        lambda t=text: self.send_text(t),
                        suppress=True,
                        trigger_on_release=True,
                    )
                except Exception:
                    pass

            self.refresh_macro_list()
            self.update_status()

            # If we loaded from legacy Roaming, immediately persist to the new location.
            if migrated:
                self.save_binds()
                self.status_bar.config(
                    text=f"✨ Migrated macros to {self.config_file}",
                    fg="#00d4aa"
                )

        except json.JSONDecodeError:
            # Corrupted JSON → reset to a clean default file so the app still runs.
            self.binds = {}
            self.auto_enter.set(False)
            self.save_binds()
            self.refresh_macro_list()
            self.update_status()
            messagebox.showwarning(
                "Reset keybinds.json",
                "File keybinds.json rusak / tidak valid.\n\n"
                "File telah di-reset ke kondisi kosong (tanpa macro)."
            )
        except Exception as e:
            messagebox.showerror(
                "Load Error",
                "Gagal load keybinds.json\n\n"
                f"Path: {self.config_file}\n"
                f"Error: {e}"
            )
    
    def update_status(self):
        count = len(self.binds)
        if self.is_paused:
            self.status_bar.config(
                text=f"⏸ Paused • Status: Stopped • {count} macro{'s' if count != 1 else ''} loaded",
                fg="#ffa726",
            )
        else:
            self.status_bar.config(
                text=f"▶ Playing • Status: Playing • {count} macro{'s' if count != 1 else ''} loaded",
                fg="#00d4aa",
            )
            
    def run(self):
        self.root.mainloop()


_single_instance_socket = None


def _acquire_single_instance_lock():
    """
    Cegah aplikasi dibuka dua kali.

    Kita pakai TCP port lokal sebagai "lock".
    Instance pertama berhasil bind ke port → lanjut jalan.
    Instance kedua gagal bind → artinya sudah ada yang jalan.
    """
    global _single_instance_socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port arbitrer, kecil kemungkinan dipakai app lain.
        s.bind(("127.0.0.1", 49327))
        s.listen(1)
        _single_instance_socket = s
        return True
    except OSError:
        return False


if __name__ == "__main__":
    if not _acquire_single_instance_lock():
        # Tampilkan pesan sederhana lalu keluar.
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                0,
                "TEXT MACRO KEYBINDER BY MIFUZI is already running.\n\n"
                "Please close the existing window before starting a new one.",
                "Already Running",
                0x10,  # MB_ICONERROR
            )
        except Exception:
            print("TEXT MACRO KEYBINDER BY MIFUZI is already running.")
        sys.exit(0)

    app = ModernKeybindManager()
    app.run()