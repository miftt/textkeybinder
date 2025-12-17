import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import keyboard
import json
import os
import sys
import threading
import time
import socket

class ModernKeybindManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TEXT MACRO KEYBINDER BY MIFUZI")
        # Default tampilan dibuat kompak tapi tinggi cukup agar semua elemen terlihat.
        self.root.geometry("900x600")
        # Boleh dikecilkan tapi tidak kurang dari 500x600 agar layout tetap rapi.
        self.root.minsize(900, 600)
        self.root.configure(bg="#1e1e1e")
        
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
        # Main container
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDEBAR - Macro List (dibuat lebih ramping supaya muat di 500x500)
        left_frame = tk.Frame(main_container, bg="#252525", width=230)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=0, pady=0)
        left_frame.pack_propagate(False)
        
        # Sidebar Header
        header = tk.Frame(left_frame, bg="#FF5722", height=45)
        header.pack(fill=tk.X)
        tk.Label(header, text="TEXT MACROS", font=("Arial", 11, "bold"), 
                bg="#FF5722", fg="white").pack(pady=10)
        
        # Macro List Container with Scrollbar
        list_container = tk.Frame(left_frame, bg="#252525")
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.macro_canvas = tk.Canvas(list_container, bg="#252525", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.macro_canvas.yview)
        self.macro_frame = tk.Frame(self.macro_canvas, bg="#252525")
        
        self.macro_frame.bind("<Configure>", lambda e: self.macro_canvas.configure(scrollregion=self.macro_canvas.bbox("all")))
        self.macro_canvas.create_window((0, 0), window=self.macro_frame, anchor="nw")
        self.macro_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.macro_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add New Macro Button
        btn_frame = tk.Frame(left_frame, bg="#252525")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="+ Add New Macro", command=self.add_new_macro,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2", pady=8).pack(fill=tk.X)
        
        # RIGHT PANEL - Editor (scrollable supaya tetap bisa diakses di window kecil)
        right_frame = tk.Frame(main_container, bg="#2d2d2d")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)

        right_canvas = tk.Canvas(right_frame, bg="#2d2d2d", highlightthickness=0)
        right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)

        right_inner = tk.Frame(right_canvas, bg="#2d2d2d")
        right_inner.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        right_canvas.create_window((0, 0), window=right_inner, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Editor Header
        editor_header = tk.Frame(right_inner, bg="#2d2d2d", height=40)
        editor_header.pack(fill=tk.X, padx=12, pady=(8, 4))
        
        tk.Label(editor_header, text="TEXT MACRO EDITOR", font=("Arial", 14, "bold"),
                bg="#2d2d2d", fg="#ffffff").pack(anchor="w")
        
        # Label/Name Input
        label_frame = tk.Frame(right_inner, bg="#2d2d2d")
        label_frame.pack(fill=tk.X, padx=12, pady=4)
        
        tk.Label(label_frame, text="Macro Name:", font=("Arial", 10),
                bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        
        self.label_entry = tk.Entry(label_frame, font=("Arial", 11), bg="#3c3c3c",
                                    fg="white", insertbackground="white", relief=tk.FLAT,
                                    highlightthickness=1, highlightbackground="#555555")
        self.label_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        tk.Label(label_frame, text="(Contoh: Mute Command, Welcome Message)", 
                font=("Arial", 8), bg="#2d2d2d", fg="#666666").pack(anchor="w", pady=(2, 0))
        
        # Key Input (Dropdown/Combobox)
        key_frame = tk.Frame(right_inner, bg="#2d2d2d")
        key_frame.pack(fill=tk.X, padx=12, pady=4)
        
        tk.Label(key_frame, text="Hotkey:", font=("Arial", 10),
                bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        
        # Style untuk Combobox agar sesuai dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.TCombobox",
                       fieldbackground="#3c3c3c",
                       background="#3c3c3c",
                       foreground="white",
                       borderwidth=1,
                       relief="flat",
                       arrowcolor="#aaaaaa",
                       darkcolor="#3c3c3c",
                       lightcolor="#3c3c3c")
        style.map("Dark.TCombobox",
                 fieldbackground=[("readonly", "#3c3c3c")],
                 background=[("readonly", "#3c3c3c")],
                 foreground=[("readonly", "white")],
                 arrowcolor=[("readonly", "#aaaaaa")],
                 bordercolor=[("readonly", "#555555")],
                 darkcolor=[("readonly", "#3c3c3c")],
                 lightcolor=[("readonly", "#3c3c3c")])
        
        self.key_entry = ttk.Combobox(key_frame, 
                                      values=self.available_hotkeys,
                                      font=("Consolas", 11),
                                      style="Dark.TCombobox",
                                      state="readonly",  # Readonly agar user tinggal pilih
                                      height=15)  # Height untuk dropdown list (jumlah item yang terlihat saat dibuka)
        self.key_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        tk.Label(key_frame, text="(Klik dropdown di atas untuk pilih hotkey, bisa di-scroll)", 
                font=("Arial", 8), bg="#2d2d2d", fg="#666666").pack(anchor="w", pady=(2, 0))
        
        # Text Content
        text_frame = tk.Frame(right_inner, bg="#2d2d2d")
        text_frame.pack(fill=tk.BOTH, expand=False, padx=12, pady=4)
        
        tk.Label(text_frame, text="Text Content:", font=("Arial", 10),
                bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        
        self.text_editor = scrolledtext.ScrolledText(
            text_frame, font=("Consolas", 9), bg="#3c3c3c", fg="white",
            insertbackground="white", relief=tk.FLAT, wrap=tk.WORD,
            highlightthickness=1, highlightbackground="#555555", height=6
        )
        self.text_editor.pack(fill=tk.BOTH, expand=False, pady=(4, 0))
        
        # Options
        options_frame = tk.Frame(right_inner, bg="#2d2d2d")
        options_frame.pack(fill=tk.X, padx=12, pady=4)
        
        auto_check = tk.Checkbutton(options_frame, text="Auto Enter (press Enter after text)",
                                   variable=self.auto_enter, font=("Arial", 9),
                                   bg="#2d2d2d", fg="#aaaaaa", selectcolor="#3c3c3c",
                                   activebackground="#2d2d2d", activeforeground="white")
        auto_check.pack(anchor="w")
        
        # Action Buttons
        action_frame = tk.Frame(right_inner, bg="#2d2d2d")
        action_frame.pack(fill=tk.X, padx=12, pady=(6, 10))
        
        tk.Button(action_frame, text="💾 Save Macro", command=self.save_current_macro,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2", width=15, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(action_frame, text="🗑 Delete", command=self.delete_current_macro,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2", width=12, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        # Simpan reference ke tombol pause supaya bisa ganti teks/warna sesuai status.
        self.pause_button = tk.Button(
            action_frame,
            text="⏸ Pause",
            command=self.toggle_pause,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            pady=8,
        )
        self.pause_button.pack(side=tk.LEFT)
        
        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready • 0 macros loaded",
                                   font=("Arial", 9), bg="#1a1a1a", fg="#4CAF50",
                                   anchor="w", padx=20, pady=8)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_macro_item(self, key, data):
        item = tk.Frame(self.macro_frame, bg="#353535", cursor="hand2")
        item.pack(fill=tk.X, pady=2, padx=4)
        
        # Icon
        icon_label = tk.Label(item, text="⌨", font=("Arial", 14),
                             bg="#353535", fg="#FF5722", width=2)
        icon_label.pack(side=tk.LEFT, padx=(8, 10), pady=10)
        
        # Content
        content_frame = tk.Frame(item, bg="#353535")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=6, padx=(0, 6))
        
        # Label/Name (nama macro yang kamu isi di kanan)
        label = data.get("label", "Unnamed Macro")
        title = tk.Label(
            content_frame,
            text=f"Name: {label}",
            font=("Arial", 10, "bold"),
            bg="#353535",
            fg="white",
            anchor="w",
        )
        title.pack(fill=tk.X)
        
        # Hotkey (tombol pemicu, mis: ., F1, ctrl+a)
        hotkey_label = tk.Label(
            content_frame,
            text=f"Hotkey: {key}",
            font=("Arial", 8),
            bg="#353535",
            fg="#FF9800",
            anchor="w",
        )
        hotkey_label.pack(fill=tk.X)
        
        # Preview isi Text Content (potongan depan saja)
        text = data.get("text", "")
        preview = text[:45] + "..." if len(text) > 45 else text
        subtitle = tk.Label(
            content_frame,
            text=f"Text: {preview}",
            font=("Arial", 8),
            bg="#353535",
            fg="#888888",
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
        for w in widgets:
            try:
                w.config(bg="#404040")
            except:
                pass
    
    def hover_out(self, widgets):
        for w in widgets:
            try:
                w.config(bg="#353535")
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
                self.pause_button.config(text="▶ Play", bg="#4CAF50")
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
                self.pause_button.config(text="⏸ Pause", bg="#FF9800")
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
                    text=f"✓ Migrated macros to {self.config_file}",
                    fg="#4CAF50"
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
                fg="#FF9800",
            )
        else:
            self.status_bar.config(
                text=f"▶ Playing • Status: Playing • {count} macro{'s' if count != 1 else ''} loaded",
                fg="#4CAF50",
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