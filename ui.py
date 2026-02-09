"""
اِبْتَسِم (Smile) - Multimedia Download Manager
Enhanced UI with theme support, custom colors, and improved layout
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading

from queue_system import (
    add_to_queue,
    add_multiple,
    worker,
    pause,
    resume,
    cancel,
    get_queue_size,
    get_status_snapshot,
    set_show_speed,
    get_show_speed,
)
from playlist_system import extract_playlist
from theme import get_theme_manager

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")

# Audio paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATHS = [
    os.path.join(SCRIPT_DIR, "assets", "splash_sound.wav"),
    os.path.join(os.path.dirname(SCRIPT_DIR), "IbtesmUltra", "assets", "splash_sound.wav"),
    os.path.join(os.path.expanduser("~"), "Desktop", "splash_sound.wav"),
]


def _get_audio_path():
    for p in AUDIO_PATHS:
        if os.path.isfile(p):
            return p
    return None


def _play_prayer_sound():
    """Play 'Pray upon the Prophet' audio (non-blocking)."""
    path = _get_audio_path()
    if not path:
        return
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            import subprocess
            subprocess.Popen(["aplay", path] if sys.platform != "darwin" else ["afplay", path], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def launch_ui():
    root = tk.Tk()
    root.title("اِبْتَسِم - Smile | Multimedia Download Manager")
    root.geometry("1000x900")
    root.minsize(850, 750)
    
    # Hide from taskbar on Windows
    if sys.platform == "win32":
        root.attributes('-toolwindow', False)
    
    # Set application icon
    icon_path = os.path.join(SCRIPT_DIR, "assets", "ibtesm.ico")
    if os.path.isfile(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass
    
    # Initialize theme manager
    theme_manager = get_theme_manager()
    C = theme_manager.get_all_colors()
    
    root.configure(bg=C["bg_dark"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TProgressbar", troughcolor=C["bg_mid"], background=C["gold"], thickness=14)
    style.configure("TCombobox", fieldbackground=C["bg_card"], background=C["bg_card"])

    percent_var = tk.StringVar(value="0%")
    status_var = tk.StringVar(value="Ready")
    path_var = tk.StringVar(value=DOWNLOAD_PATH)

    def progress_hook(d):
        if d.get("status") == "downloading":
            percent_var.set(d.get("_percent_str", "0%"))
            status_var.set("Downloading...")
        elif d.get("status") == "finished":
            percent_var.set("100%")
            status_var.set("✅ Completed")
        elif d.get("status") == "error":
            status_var.set("❌ Error: " + d.get("error", "Unknown")[:50])

    def browse_path():
        folder = filedialog.askdirectory(initialdir=path_var.get())
        if folder:
            path_var.set(folder)

    def start_download():
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a URL.")
            return
        selected_format = format_combo.get()
        add_to_queue(url, quality_combo.get(), selected_format if selected_format else "MP4")
        status_var.set(f"✓ In queue ({get_queue_size()} items)")
        url_entry.delete(0, tk.END)

    def add_multiple_urls():
        win = tk.Toplevel(root)
        win.title("Add Multiple URLs")
        win.geometry("550x450")
        win.configure(bg=C["bg_mid"])
        
        tk.Label(win, text="Enter URLs (one per line):", fg=C["text"], bg=C["bg_mid"],
                 font=("Segoe UI", 11, "bold")).pack(pady=12)
        text = scrolledtext.ScrolledText(win, height=14, width=62, bg=C["bg_card"], fg=C["text"],
                                         insertbackground=C["gold"], font=("Consolas", 10))
        text.pack(pady=10, padx=15, fill="both", expand=True)
        
        def do_add():
            urls = [l.strip() for l in text.get("1.0", tk.END).splitlines() if l.strip()]
            add_multiple(urls, quality_combo.get(), format_combo.get())
            status_var.set(f"✓ In queue ({get_queue_size()} items)")
            win.destroy()
        
        tk.Button(win, text="✓ Add to Queue", command=do_add, bg=C["gold"], fg=C["bg_dark"],
                  font=("Segoe UI", 11, "bold"), padx=25, pady=8, activebackground=C["gold_light"],
                  relief="flat", cursor="hand2").pack(pady=15)

    def open_playlist():
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a playlist URL.")
            return
        extract_playlist(url, quality_combo.get(), format_combo.get())

    def open_theme_selector():
        """Open theme selection window."""
        theme_win = tk.Toplevel(root)
        theme_win.title("Select Theme - اِبْتَسِم")
        theme_win.geometry("400x350")
        theme_win.configure(bg=C["bg_mid"])
        
        tk.Label(theme_win, text="👨‍🎨 Color Themes", fg=C["gold"], bg=C["bg_mid"],
                font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        frame = tk.Frame(theme_win, bg=C["bg_mid"])
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        def select_theme(theme_name):
            theme_manager.set_theme(theme_name)
            messagebox.showinfo("Theme Changed", f"Theme changed to {theme_name.replace('_', ' ').title()}!\nRestart app to apply.")
            theme_win.destroy()
        
        for theme_name in theme_manager.get_theme_names():
            btn = tk.Button(
                frame,
                text=theme_name.replace("_", " ").title(),
                command=lambda tn=theme_name: select_theme(tn),
                bg=C["bg_card"],
                fg=C["gold"],
                font=("Segoe UI", 10),
                padx=15,
                pady=8,
                relief="flat",
                activebackground=C["gold"],
                activeforeground=C["bg_dark"],
                cursor="hand2"
            )
            btn.pack(fill="x", pady=5)

    speed_btn = [None]

    def toggle_speed():
        v = not get_show_speed()
        set_show_speed(v)
        if speed_btn[0]:
            speed_btn[0].config(text="📊 Speed: ON" if v else "📊 Speed: OFF")

    def refresh_status_panels():
        q, d, c, s = get_status_snapshot()
        queued_list.delete(0, tk.END)
        for item in q:
            t = item.get('title', '')[:60]
            queued_list.insert(tk.END, f"  ▪ {t}{'...' if len(item.get('title', '')) > 60 else ''}")
        
        if d:
            down_text = d.get("title", "")[:50]
            if get_show_speed() and d.get("speed"):
                down_text += f"\n  📊 {d.get('speed')}"
            downloading_var.set(down_text)
        else:
            downloading_var.set("—")
        
        completed_list.delete(0, tk.END)
        for item in c[-20:]:
            title = item.get('title', '')[:60]
            completed_list.insert(tk.END, f"  ✓ {title}{'...' if len(item.get('title', '')) > 60 else ''}")
        
        root.after(600, refresh_status_panels)

    # ========== HEADER ==========
    header = tk.Frame(root, bg=C["bg_dark"])
    header.pack(fill="x", pady=(20, 12))
    
    # Top bar with icon and title
    top_bar = tk.Frame(header, bg=C["bg_dark"])
    top_bar.pack(fill="x", padx=25, pady=(0, 10))
    
    # Add icon to top left if PIL is available
    icon_display = None
    if HAS_PIL:
        icon_path = os.path.join(SCRIPT_DIR, "assets", "ibtesm.ico")
        if os.path.isfile(icon_path):
            try:
                img = Image.open(icon_path)
                img.thumbnail((48, 48), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(top_bar, image=icon_photo, bg=C["bg_dark"])
                icon_label.image = icon_photo
                icon_label.pack(side="left", padx=(0, 12))
                icon_display = icon_label
            except Exception:
                pass
    
    # Title in top bar
    title_frame = tk.Frame(top_bar, bg=C["bg_dark"])
    title_frame.pack(side="left", fill="both", expand=True)
    
    tk.Label(
        header,
        text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        fg=C["gold"],
        bg=C["bg_dark"],
        font=("Traditional Arabic", 22, "bold")
    ).pack(pady=(0, 8))
    
    tk.Label(
        header,
        text="صَلِّ عَلَى النَّبِيِّ ﷺ",
        fg=C["gold_light"],
        bg=C["bg_dark"],
        font=("Traditional Arabic", 20, "bold")
    ).pack(pady=2)

    # ========== URL INPUT SECTION ==========
    url_frame = tk.Frame(root, bg=C["bg_dark"])
    url_frame.pack(fill="x", padx=25, pady=10)
    tk.Label(url_frame, text="📎 URL/Link:", fg=C["text"], bg=C["bg_dark"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
    url_entry = tk.Entry(
        url_frame,
        width=80,
        font=("Segoe UI", 11),
        bg=C["bg_card"],
        fg=C["text"],
        insertbackground=C["gold"],
        relief="flat",
        bd=0
    )
    url_entry.pack(pady=6, fill="x", ipady=10, ipadx=10)

    # ========== OPTIONS ROW ==========
    opts = tk.Frame(root, bg=C["bg_dark"])
    opts.pack(pady=12, padx=25, fill="x")
    
    tk.Label(opts, text="⚙️ Quality:", fg=C["text_muted"], bg=C["bg_dark"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
    quality_combo = ttk.Combobox(opts, values=["Best", "1440p", "1080p", "720p", "480p", "360p", "240p"], 
                                 width=8, state="readonly", font=("Segoe UI", 10))
    quality_combo.set("Best")
    quality_combo.pack(side="left", padx=(0, 20))
    
    tk.Label(opts, text="📁 Format:", fg=C["text_muted"], bg=C["bg_dark"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
    format_values = [
        "— VIDEO FORMATS —", "MP4", "WebM", "MKV", "MOV", "AVI", "FLV", "3GP", "AV1", "VP9", "H264",
        "— AUDIO FORMATS —", "MP3", "M4A", "AAC", "FLAC", "WAV", "OPUS", "OGG", "HIGH", "ULTRA"
    ]
    format_combo = ttk.Combobox(opts, values=format_values, width=12, state="readonly", font=("Segoe UI", 10))
    format_combo.set("MP4")
    format_combo.pack(side="left", padx=(0, 20))
    
    tk.Label(opts, text="💾 Save to:", fg=C["text_muted"], bg=C["bg_dark"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(20, 6))
    path_entry = tk.Entry(opts, textvariable=path_var, width=28, font=("Segoe UI", 9), bg=C["bg_card"], 
                         fg=C["text"], relief="flat", bd=0)
    path_entry.pack(side="left", padx=(0, 6), fill="x", expand=True)
    tk.Button(opts, text="📂 Browse", command=browse_path, bg=C["bg_card"], fg=C["gold"], relief="flat", 
             font=("Segoe UI", 9, "bold"), padx=10, pady=4, activebackground=C["gold"], activeforeground=C["bg_dark"],
             cursor="hand2").pack(side="left")

    # ========== BUTTONS ==========
    btn_frame = tk.Frame(root, bg=C["bg_dark"])
    btn_frame.pack(pady=12)
    
    main_btn_frame = tk.Frame(btn_frame, bg=C["bg_dark"])
    main_btn_frame.pack(pady=(0, 8))
    tk.Button(main_btn_frame, text="⬇ Download", command=start_download, bg=C["gold"], fg=C["bg_dark"],
              font=("Segoe UI", 11, "bold"), width=15, relief="flat", padx=16, pady=9, 
              activebackground=C["gold_light"], cursor="hand2").grid(row=0, column=0, padx=6)
    tk.Button(main_btn_frame, text="➕ Add Multiple", command=add_multiple_urls, bg=C["bg_card"], fg=C["gold"],
              font=("Segoe UI", 10, "bold"), width=15, relief="flat", padx=14, pady=7,
              activebackground=C["bg_card"], activeforeground=C["gold_light"], cursor="hand2").grid(row=0, column=1, padx=6)
    tk.Button(main_btn_frame, text="📋 Playlist", command=open_playlist, bg=C["bg_card"], fg=C["gold"],
              font=("Segoe UI", 10, "bold"), width=13, relief="flat", padx=12, pady=7,
              activebackground=C["bg_card"], activeforeground=C["gold_light"], cursor="hand2").grid(row=0, column=2, padx=6)
    
    control_btn_frame = tk.Frame(btn_frame, bg=C["bg_dark"])
    control_btn_frame.pack(pady=8)
    speed_btn[0] = tk.Button(control_btn_frame, text="📊 Speed: OFF", command=toggle_speed, bg=C["accent"], 
                            fg=C["text"], font=("Segoe UI", 9, "bold"), width=12, relief="flat", padx=8, pady=5,
                            activebackground=C["accent"], activeforeground=C["gold"], cursor="hand2")
    speed_btn[0].grid(row=0, column=0, padx=4)
    tk.Button(control_btn_frame, text="⏸ Pause", command=pause, bg=C["accent"], fg=C["text"], 
              font=("Segoe UI", 9, "bold"), width=12, relief="flat", padx=8, pady=5,
              activebackground=C["accent"], activeforeground=C["gold"], cursor="hand2").grid(row=0, column=1, padx=4)
    tk.Button(control_btn_frame, text="▶ Resume", command=resume, bg=C["accent"], fg=C["text"],
              font=("Segoe UI", 9, "bold"), width=12, relief="flat", padx=8, pady=5,
              activebackground=C["accent"], activeforeground=C["gold"], cursor="hand2").grid(row=0, column=2, padx=4)
    tk.Button(control_btn_frame, text="✕ Cancel", command=cancel, bg=C["bg_mid"], fg=C["error"],
              font=("Segoe UI", 9, "bold"), width=12, relief="flat", padx=8, pady=5,
              activebackground=C["error"], activeforeground=C["bg_dark"], cursor="hand2").grid(row=0, column=3, padx=4)
    tk.Button(control_btn_frame, text="🎨 Themes", command=open_theme_selector, bg=C["accent"], fg=C["text"],
              font=("Segoe UI", 9, "bold"), width=12, relief="flat", padx=8, pady=5,
              activebackground=C["accent"], activeforeground=C["gold"], cursor="hand2").grid(row=0, column=4, padx=4)

    # ========== PROGRESS ==========
    prog_frame = tk.Frame(root, bg=C["bg_dark"])
    prog_frame.pack(fill="x", padx=25, pady=10)
    
    status_info_frame = tk.Frame(prog_frame, bg=C["bg_dark"])
    status_info_frame.pack(fill="x", pady=(0, 4))
    tk.Label(status_info_frame, textvariable=status_var, fg=C["text_muted"], bg=C["bg_dark"], 
            font=("Segoe UI", 10)).pack(anchor="w")
    tk.Label(status_info_frame, textvariable=percent_var, fg=C["gold"], bg=C["bg_dark"], 
            font=("Segoe UI", 13, "bold")).pack(anchor="e")
    
    progress_bar = ttk.Progressbar(prog_frame, length=500, mode="determinate")
    progress_bar.pack(pady=8, fill="x", ipady=2)

    def update_progress():
        try:
            pct_str = percent_var.get().replace("%", "").strip()
            pct = float(pct_str) if pct_str and pct_str.replace(".", "").isdigit() else 0
            progress_bar["value"] = min(100, max(0, pct))
        except (ValueError, AttributeError):
            pass
        root.after(400, update_progress)
    update_progress()

    # ========== STATUS SECTIONS ==========
    sections_frame = tk.Frame(root, bg=C["bg_dark"])
    sections_frame.pack(fill="both", expand=True, padx=20, pady=10)

    q_frame = tk.LabelFrame(sections_frame, text="📥 In Queue", fg=C["gold"], bg=C["bg_dark"], 
                           font=("Segoe UI", 10, "bold"), padx=6, pady=6)
    q_frame.pack(side="left", fill="both", expand=True, padx=5)
    queued_list = tk.Listbox(q_frame, height=6, bg=C["bg_card"], fg=C["text"], selectbackground=C["accent"],
                            font=("Consolas", 9), relief="flat", bd=0)
    queued_list.pack(fill="both", expand=True)

    d_frame = tk.LabelFrame(sections_frame, text="⬇️ Downloading", fg=C["gold"], bg=C["bg_dark"],
                           font=("Segoe UI", 10, "bold"), padx=6, pady=6)
    d_frame.pack(side="left", fill="both", expand=True, padx=5)
    downloading_var = tk.StringVar(value="—")
    tk.Label(d_frame, textvariable=downloading_var, fg=C["text"], bg=C["bg_card"], font=("Consolas", 9),
            wraplength=240, justify="left", padx=12, pady=12, relief="flat").pack(fill="both", expand=True)

    c_frame = tk.LabelFrame(sections_frame, text="✅ Completed", fg=C["gold_light"], bg=C["bg_dark"],
                           font=("Segoe UI", 10, "bold"), padx=6, pady=6)
    c_frame.pack(side="left", fill="both", expand=True, padx=5)
    completed_list = tk.Listbox(c_frame, height=6, bg=C["bg_card"], fg=C["text"], selectbackground=C["accent"],
                               font=("Consolas", 9), relief="flat", bd=0)
    completed_list.pack(fill="both", expand=True)

    # ========== FOOTER ==========
    footer = tk.Frame(root, bg=C["bg_dark"])
    footer.pack(fill="x", side="bottom", pady=8)
    tk.Label(footer, text="🙏 Developer: Ahmed Al-Amawy  |  Made with ❤️", fg=C["text_muted"], bg=C["bg_dark"],
            font=("Segoe UI", 8)).pack(side="right", padx=25)

    root.after(4000, _play_prayer_sound)

    def repeat_prayer_sound():
        _play_prayer_sound()
        root.after(180000, repeat_prayer_sound)

    root.after(4000 + 180000, repeat_prayer_sound)

    def path_getter():
        return path_var.get()

    threading.Thread(target=worker, args=(path_getter, progress_hook), daemon=True).start()
    refresh_status_panels()

    root.mainloop()
