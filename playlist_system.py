"""
Playlist extraction with thumbnails and improved formatting.
Theme-aware UI for consistency.
"""

import tkinter as tk
from tkinter import ttk
import io
import yt_dlp
import requests
from queue_system import add_to_queue
from theme import get_theme_manager
from PIL import Image, ImageTk


def _get_thumbnail_url(vid_id: str, url: str) -> str:
    """Get thumbnail URL for video. YouTube: img.youtube.com/vi/ID/mqdefault.jpg"""
    if vid_id and ("youtube" in url or "youtu.be" in url):
        return f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg"
    return None


def _load_thumbnail(url: str, size=(160, 90)) -> ImageTk.PhotoImage:
    """Load and resize thumbnail from URL."""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content))
        img = img.convert("RGB")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def extract_playlist(url: str, quality: str, media_format: str):
    """Open a playlist selector window with thumbnails."""
    try:
        ydl_opts = {"quiet": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        _show_error(str(e))
        return

    entries = info.get("entries", [])
    if not entries:
        _show_error("No entries found in playlist.")
        return

    win = tk.Toplevel()
    win.title("Playlist Manager - اِبْتَسِم")
    win.geometry("850x580")
    
    # Get theme colors
    theme_manager = get_theme_manager()
    C = theme_manager.get_all_colors()
    
    win.configure(bg=C["bg_dark"])

    tk.Label(
        win,
        text="📋 Select videos to download",
        fg=C["gold"],
        bg=C["bg_dark"],
        font=("Segoe UI", 14, "bold")
    ).pack(pady=14)

    canvas = tk.Canvas(win, bg=C["bg_dark"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    container = tk.Frame(canvas, bg=C["bg_dark"])
    canvas.create_window((0, 0), window=container, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(0, 1))
    scrollbar.pack(side="right", fill="y")

    def on_frame_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))

    container.bind("<Configure>", on_frame_configure)

    vars_list = []
    thumb_refs = []

    for vid in entries:
        if not vid:
            continue
        vid_id = vid.get("id", "")
        vid_url = vid.get("url") or vid.get("webpage_url", "")
        if not vid_url and vid_id:
            vid_url = f"https://www.youtube.com/watch?v={vid_id}"
        title = vid.get("title", "Unknown")
        title_short = title[:70] + ("..." if len(title) > 70 else "")

        card = tk.Frame(container, bg=C["bg_card"], bd=0, relief="flat")
        card.pack(fill="x", padx=12, pady=6)

        inner = tk.Frame(card, bg=C["bg_card"])
        inner.pack(fill="x", padx=8, pady=8)

        var = tk.BooleanVar(value=True)
        vars_list.append((var, vid_url, title))

        # Thumbnail
        thumb_frame = tk.Frame(inner, bg=C["bg_mid"], width=160, height=90)
        thumb_frame.pack(side="left", padx=(0, 12))
        thumb_frame.pack_propagate(False)

        thumb_url = _get_thumbnail_url(vid_id, vid_url or "https://youtube.com")
        if thumb_url:
            try:
                photo = _load_thumbnail(thumb_url)
                if photo:
                    thumb_refs.append(photo)
                    lbl = tk.Label(thumb_frame, image=photo, bg=C["bg_mid"])
                    lbl.image = photo
                    lbl.pack(fill="both", expand=True)
                else:
                    _placeholder(thumb_frame, C)
            except Exception:
                _placeholder(thumb_frame, C)
        else:
            _placeholder(thumb_frame, C)

        # Title + checkbox
        text_frame = tk.Frame(inner, bg=C["bg_card"])
        text_frame.pack(side="left", fill="both", expand=True)
        cb = tk.Checkbutton(
            text_frame,
            text=title_short,
            variable=var,
            fg=C["text"],
            bg=C["bg_card"],
            selectcolor=C["bg_mid"],
            activebackground=C["bg_card"],
            activeforeground=C["gold"],
            wraplength=500,
            justify="left",
            font=("Segoe UI", 10)
        )
        cb.pack(anchor="w")

    def _placeholder(parent, colors):
        tk.Label(parent, text="🎬 No preview", fg=colors["text_muted"], bg=colors["bg_mid"], 
                font=("Segoe UI", 8)).pack(expand=True)

    container.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    btn_frame = tk.Frame(win, bg=C["bg_dark"])
    btn_frame.pack(pady=14)

    def download_selected():
        for var, video_url, _ in vars_list:
            if var.get() and video_url:
                add_to_queue(video_url, quality, media_format)
        win.destroy()

    def download_all():
        for _, video_url, _ in vars_list:
            if video_url:
                add_to_queue(video_url, quality, media_format)
        win.destroy()

    _style_btn(btn_frame, "✓ Selected", C["bg_card"], C["gold"], download_selected, C).grid(row=0, column=0, padx=8)
    _style_btn(btn_frame, "✓ All Videos", C["accent"], C["text"], download_all, C).grid(row=0, column=1, padx=8)


def _style_btn(parent, text, bg, fg, cmd, colors):
    btn = tk.Button(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 10, "bold"),
                    width=16, relief="flat", padx=12, pady=7, cursor="hand2", command=cmd,
                    activebackground=fg, activeforeground=bg)
    return btn


def _show_error(msg: str):
    theme_manager = get_theme_manager()
    C = theme_manager.get_all_colors()
    
    win = tk.Toplevel()
    win.title("❌ Error")
    win.geometry("430x120")
    win.configure(bg=C["bg_dark"])
    tk.Label(win, text=msg, fg=C["error"], bg=C["bg_dark"], wraplength=380, font=("Segoe UI", 10)).pack(pady=20, padx=20)
    tk.Button(win, text="OK", command=win.destroy, bg=C["gold"], fg=C["bg_dark"], 
              font=("Segoe UI", 10, "bold"), padx=20, pady=6, relief="flat", cursor="hand2").pack(pady=10)

