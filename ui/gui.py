"""
UI setup and components for the Keybind Manager.
Handles all GUI creation and styling with glassmorphism theme.
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
from config import COLORS

# Try to import ttkbootstrap
try:
    import ttkbootstrap as ttkb
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    ttkb = None


def setup_gui(app):
    """Setup all GUI components for the application."""
    # Main container dengan gradient background effect (glassmorphism base)
    main_container = tk.Frame(app.root, bg=COLORS["bg_main"])
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # LEFT SIDEBAR - Macro List dengan glassmorphism effect
    left_frame = tk.Frame(main_container, bg=COLORS["bg_sidebar"], width=260)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=12, pady=12)
    left_frame.pack_propagate(False)
    
    # Sidebar Header dengan gradient effect (modern genz style)
    header = tk.Frame(left_frame, bg=COLORS["bg_header"], height=55)
    header.pack(fill=tk.X, padx=0, pady=0)
    tk.Label(header, text="✨ TEXT MACROS", font=("Segoe UI", 13, "bold"), 
            bg=COLORS["bg_header"], fg=COLORS["text_primary"]).pack(pady=15)
    
    # Macro List Container with Scrollbar (glass effect)
    list_container = tk.Frame(left_frame, bg=COLORS["bg_sidebar"])
    list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    
    app.macro_canvas = tk.Canvas(list_container, bg=COLORS["bg_sidebar"], highlightthickness=0)
    scrollbar = tk.Scrollbar(list_container, orient="vertical", command=app.macro_canvas.yview,
                             bg="#2a2a3e", troughcolor=COLORS["bg_sidebar"], activebackground="#3a3a4e",
                             width=10, borderwidth=0)
    app.macro_frame = tk.Frame(app.macro_canvas, bg=COLORS["bg_sidebar"])
    
    app.macro_frame.bind("<Configure>", lambda e: app.macro_canvas.configure(scrollregion=app.macro_canvas.bbox("all")))
    app.macro_canvas.create_window((0, 0), window=app.macro_frame, anchor="nw")
    app.macro_canvas.configure(yscrollcommand=scrollbar.set)
    
    app.macro_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Add New Macro Button (modern glassmorphism button)
    btn_frame = tk.Frame(left_frame, bg=COLORS["bg_sidebar"])
    btn_frame.pack(fill=tk.X, padx=8, pady=8)
    
    if app.use_ttkbootstrap:
        add_btn = ttkb.Button(btn_frame, text="✨ + Add New Macro", command=app.add_new_macro,
                             bootstyle="success", width=20)
        add_btn.pack(fill=tk.X, pady=2)
    else:
        add_btn = tk.Button(btn_frame, text="✨ + Add New Macro", command=app.add_new_macro,
                 bg=COLORS["accent_teal"], fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, cursor="hand2", pady=12, activebackground=COLORS["accent_teal_dark"],
                 activeforeground="white", bd=0)
        add_btn.pack(fill=tk.X)
        def add_btn_enter(e): add_btn.config(bg=COLORS["accent_teal_dark"])
        def add_btn_leave(e): add_btn.config(bg=COLORS["accent_teal"])
        add_btn.bind("<Enter>", add_btn_enter)
        add_btn.bind("<Leave>", add_btn_leave)
    
    # RIGHT PANEL - Editor dengan glassmorphism effect
    right_frame = tk.Frame(main_container, bg=COLORS["bg_sidebar"])
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

    right_canvas = tk.Canvas(right_frame, bg=COLORS["bg_sidebar"], highlightthickness=0)
    right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview,
                                  bg="#2a2a3e", troughcolor=COLORS["bg_sidebar"], activebackground="#3a3a4e",
                                  width=10, borderwidth=0)

    right_inner = tk.Frame(right_canvas, bg=COLORS["bg_sidebar"])
    right_inner.bind(
        "<Configure>",
        lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
    )

    right_canvas.create_window((0, 0), window=right_inner, anchor="nw")
    right_canvas.configure(yscrollcommand=right_scrollbar.set)

    right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Editor Header (modern glassmorphism style)
    editor_header = tk.Frame(right_inner, bg=COLORS["bg_header"], height=50)
    editor_header.pack(fill=tk.X, padx=0, pady=(0, 12))
    
    tk.Label(editor_header, text="🎨 TEXT MACRO EDITOR", font=("Segoe UI", 16, "bold"),
            bg=COLORS["bg_header"], fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=15)
    
    # Label/Name Input (glassmorphism card)
    label_frame = tk.Frame(right_inner, bg=COLORS["bg_card"])
    label_frame.pack(fill=tk.X, padx=16, pady=8)
    
    tk.Label(label_frame, text="Macro Name", font=("Segoe UI", 10, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))
    
    app.label_entry = tk.Entry(label_frame, font=("Segoe UI", 11), bg=COLORS["bg_input"],
                                fg=COLORS["text_primary"], insertbackground=COLORS["accent_teal"], relief=tk.FLAT,
                                highlightthickness=2, highlightbackground=COLORS["accent_teal"],
                                highlightcolor=COLORS["accent_teal"], bd=0)
    app.label_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
    
    tk.Label(label_frame, text="💡 Contoh: Mute Command, Welcome Message", 
            font=("Segoe UI", 8), bg=COLORS["bg_card"], fg=COLORS["text_hint"]).pack(anchor="w")
    
    # Key Input (Dropdown/Combobox) - glassmorphism style
    key_frame = tk.Frame(right_inner, bg=COLORS["bg_card"])
    key_frame.pack(fill=tk.X, padx=16, pady=8)
    
    tk.Label(key_frame, text="Hotkey", font=("Segoe UI", 10, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))
    
    # Style untuk Combobox dengan glassmorphism effect
    if app.use_ttkbootstrap:
        app.key_entry = ttkb.Combobox(key_frame, 
                                      values=app.available_hotkeys,
                                      font=("Segoe UI", 11),
                                      bootstyle="dark",
                                      state="readonly",
                                      height=15)
        app.key_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
    else:
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Glass.TCombobox",
                       fieldbackground=COLORS["bg_input"],
                       background=COLORS["bg_input"],
                       foreground=COLORS["text_primary"],
                       borderwidth=2,
                       relief="flat",
                       arrowcolor=COLORS["accent_teal"],
                       darkcolor=COLORS["bg_input"],
                       lightcolor=COLORS["bg_input"],
                       bordercolor=COLORS["accent_teal"])
        style.map("Glass.TCombobox",
                 fieldbackground=[("readonly", COLORS["bg_input"]), ("active", COLORS["bg_input"])],
                 background=[("readonly", COLORS["bg_input"]), ("active", COLORS["bg_input"])],
                 foreground=[("readonly", COLORS["text_primary"]), ("active", COLORS["text_primary"])],
                 arrowcolor=[("readonly", COLORS["accent_teal"]), ("active", COLORS["accent_teal"])],
                 bordercolor=[("readonly", COLORS["accent_teal"]), ("active", COLORS["accent_teal"])],
                 darkcolor=[("readonly", COLORS["bg_input"]), ("active", COLORS["bg_input"])],
                 lightcolor=[("readonly", COLORS["bg_input"]), ("active", COLORS["bg_input"])])
        
        app.key_entry = ttk.Combobox(key_frame, 
                                      values=app.available_hotkeys,
                                      font=("Segoe UI", 11),
                                      style="Glass.TCombobox",
                                      state="readonly",
                                      height=15)
        app.key_entry.pack(fill=tk.X, pady=(0, 4), ipady=10, ipadx=12)
    
    tk.Label(key_frame, text="💡 Klik dropdown untuk pilih hotkey (scrollable)", 
            font=("Segoe UI", 8), bg=COLORS["bg_card"], fg=COLORS["text_hint"]).pack(anchor="w")
    
    # Text Content - glassmorphism card
    text_frame = tk.Frame(right_inner, bg=COLORS["bg_card"])
    text_frame.pack(fill=tk.BOTH, expand=False, padx=16, pady=8)
    
    tk.Label(text_frame, text="Text Content", font=("Segoe UI", 10, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))
    
    app.text_editor = scrolledtext.ScrolledText(
        text_frame, font=("Consolas", 10), bg=COLORS["bg_input"], fg=COLORS["text_primary"],
        insertbackground=COLORS["accent_teal"], relief=tk.FLAT, wrap=tk.WORD,
        highlightthickness=2, highlightbackground=COLORS["accent_teal"],
        highlightcolor=COLORS["accent_teal"], height=8, bd=0,
        selectbackground=COLORS["accent_teal"], selectforeground=COLORS["bg_main"]
    )
    app.text_editor.pack(fill=tk.BOTH, expand=False, pady=(0, 4), ipadx=12, ipady=8)
    
    # Options - glassmorphism style
    options_frame = tk.Frame(right_inner, bg=COLORS["bg_card"])
    options_frame.pack(fill=tk.X, padx=16, pady=8)
    
    auto_check = tk.Checkbutton(options_frame, text="✨ Auto Enter (press Enter after text)",
                               variable=app.auto_enter, font=("Segoe UI", 10),
                               bg=COLORS["bg_card"], fg=COLORS["text_secondary"], selectcolor=COLORS["accent_teal"],
                               activebackground=COLORS["bg_card"], activeforeground=COLORS["accent_teal"],
                               highlightbackground=COLORS["bg_card"])
    auto_check.pack(anchor="w")

    # Typing speed control (manual)
    speed_frame = tk.Frame(options_frame, bg=COLORS["bg_card"])
    speed_frame.pack(fill=tk.X, pady=(6, 0))

    tk.Label(
        speed_frame,
        text="Typing Speed (seconds per character)",
        font=("Segoe UI", 9, "bold"),
        bg=COLORS["bg_card"],
        fg=COLORS["text_secondary"],
    ).pack(anchor="w")

    speed_entry = tk.Entry(
        speed_frame,
        textvariable=app.per_char_delay,
        font=("Segoe UI", 10),
        bg=COLORS["bg_input"],
        fg=COLORS["text_primary"],
        insertbackground=COLORS["accent_teal"],
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=COLORS["accent_teal"],
        highlightcolor=COLORS["accent_teal"],
        bd=0,
        width=10,
    )
    speed_entry.pack(anchor="w", pady=(2, 0), ipadx=6, ipady=4)

    tk.Label(
        speed_frame,
        text="Default: 0.03 • Semakin kecil = lebih cepat (bisa typo), semakin besar = lebih stabil.",
        font=("Segoe UI", 8),
        bg=COLORS["bg_card"],
        fg=COLORS["text_hint"],
    ).pack(anchor="w", pady=(2, 0))
    
    # Action Buttons - modern glassmorphism buttons
    action_frame = tk.Frame(right_inner, bg=COLORS["bg_card"])
    action_frame.pack(fill=tk.X, padx=16, pady=(12, 16))
    
    if app.use_ttkbootstrap:
        save_btn = ttkb.Button(action_frame, text="💾 Save Macro", command=app.save_current_macro,
                     bootstyle="success", width=20)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttkb.Button(action_frame, text="🗑 Delete", command=app.delete_current_macro,
                     bootstyle="danger", width=18)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        app.pause_button = ttkb.Button(
            action_frame,
            text="⏸ Pause",
            command=app.toggle_pause,
            bootstyle="warning",
            width=20
        )
        app.pause_button.pack(side=tk.LEFT)
    else:
        save_btn = tk.Button(action_frame, text="💾 Save Macro", command=app.save_current_macro,
                 bg=COLORS["accent_teal"], fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, cursor="hand2", width=18, pady=12, bd=0,
                 activebackground=COLORS["accent_teal_dark"], activeforeground="white")
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        def save_btn_enter(e): save_btn.config(bg=COLORS["accent_teal_dark"])
        def save_btn_leave(e): save_btn.config(bg=COLORS["accent_teal"])
        save_btn.bind("<Enter>", save_btn_enter)
        save_btn.bind("<Leave>", save_btn_leave)
        
        delete_btn = tk.Button(action_frame, text="🗑 Delete", command=app.delete_current_macro,
                 bg=COLORS["accent_red"], fg="white", font=("Segoe UI", 11, "bold"),
                 relief=tk.FLAT, cursor="hand2", width=15, pady=12, bd=0,
                 activebackground=COLORS["accent_red_dark"], activeforeground="white")
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        def delete_btn_enter(e): delete_btn.config(bg=COLORS["accent_red_dark"])
        def delete_btn_leave(e): delete_btn.config(bg=COLORS["accent_red"])
        delete_btn.bind("<Enter>", delete_btn_enter)
        delete_btn.bind("<Leave>", delete_btn_leave)
        
        app.pause_button = tk.Button(
            action_frame,
            text="⏸ Pause",
            command=app.toggle_pause,
            bg=COLORS["accent_orange"],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            width=18,
            pady=12,
            bd=0,
            activebackground=COLORS["accent_orange_dark"],
            activeforeground="white"
        )
        app.pause_button.pack(side=tk.LEFT)
        def pause_btn_enter(e): 
            if not app.is_paused:
                app.pause_button.config(bg=COLORS["accent_orange_dark"])
        def pause_btn_leave(e): 
            if not app.is_paused:
                app.pause_button.config(bg=COLORS["accent_orange"])
        app.pause_button.bind("<Enter>", pause_btn_enter)
        app.pause_button.bind("<Leave>", pause_btn_leave)
    
    # Status Bar - modern glassmorphism style
    app.status_bar = tk.Label(app.root, text="✨ Ready • Status: Playing • 0 macros loaded",
                               font=("Segoe UI", 10), bg=COLORS["bg_header"], fg=COLORS["accent_teal"],
                               anchor="w", padx=20, pady=12)
    app.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


def create_macro_item(app, key, data):
    """Create a macro item card in the sidebar list."""
    # Glassmorphism card style
    item = tk.Frame(app.macro_frame, bg=COLORS["bg_card"], cursor="hand2", relief=tk.FLAT, bd=0)
    item.pack(fill=tk.X, pady=6, padx=4)
    
    # Icon dengan modern style
    icon_label = tk.Label(item, text="⌨", font=("Segoe UI", 16),
                         bg=COLORS["bg_card"], fg=COLORS["accent_teal"], width=2)
    icon_label.pack(side=tk.LEFT, padx=(12, 12), pady=12)
    
    # Content dengan glassmorphism
    content_frame = tk.Frame(item, bg=COLORS["bg_card"])
    content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(0, 10))
    
    # Label/Name
    label = data.get("label", "Unnamed Macro")
    title = tk.Label(
        content_frame,
        text=f"Name: {label}",
        font=("Segoe UI", 11, "bold"),
        bg=COLORS["bg_card"],
        fg=COLORS["text_primary"],
        anchor="w",
    )
    title.pack(fill=tk.X, pady=(0, 2))
    
    # Hotkey
    hotkey_label = tk.Label(
        content_frame,
        text=f"Hotkey: {key}",
        font=("Segoe UI", 9),
        bg=COLORS["bg_card"],
        fg=COLORS["accent_teal"],
        anchor="w",
    )
    hotkey_label.pack(fill=tk.X, pady=(0, 2))
    
    # Preview isi Text Content
    text = data.get("text", "")
    preview = text[:45] + "..." if len(text) > 45 else text
    subtitle = tk.Label(
        content_frame,
        text=f"Text: {preview}",
        font=("Segoe UI", 8),
        bg=COLORS["bg_card"],
        fg=COLORS["text_secondary"],
        anchor="w",
    )
    subtitle.pack(fill=tk.X)
    
    # Bind click event
    for widget in [item, icon_label, content_frame, title, hotkey_label, subtitle]:
        widget.bind("<Button-1>", lambda e, k=key: app.select_macro(k))
        widget.bind("<Enter>", lambda e, widgets=[item, icon_label, content_frame, title, hotkey_label, subtitle]: hover_in(widgets))
        widget.bind("<Leave>", lambda e, widgets=[item, icon_label, content_frame, title, hotkey_label, subtitle]: hover_out(widgets))
    
    return item


def hover_in(widgets):
    """Modern hover effect dengan glassmorphism."""
    for w in widgets:
        try:
            if isinstance(w, tk.Frame):
                w.config(bg=COLORS["bg_hover"])
            elif isinstance(w, tk.Label):
                current_bg = w.cget("bg")
                if current_bg == COLORS["bg_card"]:
                    w.config(bg=COLORS["bg_hover"])
                elif current_bg == COLORS["accent_teal"]:
                    w.config(bg=COLORS["bg_hover"], fg=COLORS["accent_teal"])
        except:
            pass


def hover_out(widgets):
    """Reset ke original glassmorphism color."""
    for w in widgets:
        try:
            if isinstance(w, tk.Frame):
                w.config(bg=COLORS["bg_card"])
            elif isinstance(w, tk.Label):
                current_text = w.cget("text")
                if "Name:" in current_text:
                    w.config(bg=COLORS["bg_card"], fg=COLORS["text_primary"])
                elif "Hotkey:" in current_text:
                    w.config(bg=COLORS["bg_card"], fg=COLORS["accent_teal"])
                elif "Text:" in current_text:
                    w.config(bg=COLORS["bg_card"], fg=COLORS["text_secondary"])
                elif w.cget("text") == "⌨":
                    w.config(bg=COLORS["bg_card"], fg=COLORS["accent_teal"])
        except:
            pass

