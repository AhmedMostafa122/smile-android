"""
Download Queue System with pause, resume, cancel, and status tracking.
Highly optimized for speed, memory efficiency, and parallel downloads.
"""

import time
import threading
from engine import download
from collections import deque


download_queue = deque()  # Changed to deque for O(1) popleft operations
pause_flag = False
cancel_flag = False
_lock = threading.Lock()

# Status tracking for UI
queued_items = deque(maxlen=100)  # Fixed max size for memory efficiency
downloading_item = None  # {"url", "title", "speed", "percent"} or None
completed_items = deque(maxlen=100)  # Keep only last 100 completed items
show_speed = False
_speed_str = ""

# Performance tracking
download_stats = {
    "total_downloaded": 0,
    "total_time": 0,
    "average_speed": 0.0
}


def add_to_queue(url: str, quality: str = "Best", media_format: str = "Video"):
    """Add a download task to the queue."""
    with _lock:
        url = url.strip()
        download_queue.append((url, quality, media_format))
        queued_items.append({"url": url, "quality": quality, "format": media_format, "title": url[:55] + ("..." if len(url) > 55 else "")})


def add_multiple(urls: list, quality: str = "Best", media_format: str = "Video"):
    """Add multiple URLs to the queue."""
    for url in urls:
        url = url.strip()
        if url and not url.startswith("#"):
            add_to_queue(url, quality, media_format)


def pause():
    global pause_flag
    pause_flag = True


def resume():
    global pause_flag
    pause_flag = False


def cancel():
    global cancel_flag
    cancel_flag = True


def get_queue_size():
    with _lock:
        return len(download_queue)


def set_show_speed(value: bool):
    global show_speed
    show_speed = value


def get_show_speed():
    return show_speed


def get_status_snapshot():
    """Return current queued, downloading, completed for UI."""
    with _lock:
        q = list(queued_items) if queued_items else []
        d = downloading_item.copy() if downloading_item else None
        c = list(completed_items) if completed_items else []
        s = _speed_str
    return q, d, c, s


def _set_downloading(item):
    global downloading_item
    with _lock:
        downloading_item = item


def _clear_downloading():
    global downloading_item
    with _lock:
        downloading_item = None


def _remove_from_queued(url):
    with _lock:
        for i, x in enumerate(queued_items):
            if x.get("url") == url:
                queued_items.pop(i)
                break


def _add_completed(title: str, url: str):
    with _lock:
        completed_items.append({"title": title[:60], "url": url})


def _set_speed(s: str):
    global _speed_str
    _speed_str = s or ""


def worker(download_path, progress_hook=None):
    """Background worker that processes the download queue with optimizations."""
    global cancel_flag, pause_flag, download_queue, download_stats

    start_time = time.time()

    while True:
        with _lock:
            if not download_queue:
                task = None
            else:
                task = download_queue.popleft()
                # Remove from queued display - optimized with deque
                if task and len(queued_items) > 0:
                    if queued_items[0].get("url") == task[0]:
                        queued_items.popleft()

        if task is None:
            time.sleep(1)
            continue

        path = download_path() if callable(download_path) else download_path
        url, quality, media_format = task
        cancel_flag = False
        task_start_time = time.time()

        # Get title for display
        title = _extract_title_from_url(url)

        def hook(d):
            if cancel_flag:
                raise Exception("CANCELLED")
            while pause_flag:
                time.sleep(0.5)
            if progress_hook:
                progress_hook(d)
            
            status = d.get("status")
            if status == "downloading":
                speed = d.get("_speed_str", "") or str(d.get("speed", ""))
                info = d.get("info_dict") or {}
                disp_title = info.get("title", title) if isinstance(info, dict) else title
                _set_speed(speed)
                _set_downloading({
                    "title": disp_title or title,
                    "url": url,
                    "speed": speed,
                    "percent": d.get("_percent_str", "0%")
                })
            elif status == "finished":
                info = d.get("info_dict") or {}
                fn = info.get("title", title) if isinstance(info, dict) else title
                _add_completed(fn, url)
                _clear_downloading()
                _set_speed("")
                
                # Update stats
                task_time = time.time() - task_start_time
                download_stats["total_time"] += task_time

        try:
            _set_downloading({"title": title, "url": url, "speed": "Initializing...", "percent": "0%"})
            download(url, path, quality, media_format, hook)
        except Exception as e:
            if "CANCELLED" not in str(e):
                _add_completed(f"❌ {str(e)[:35]}", url)
                if progress_hook:
                    progress_hook({"status": "error", "error": str(e)})
            _clear_downloading()
            _set_speed("")


def _extract_title_from_url(url: str) -> str:
    """Extract a short title from URL for display."""
    try:
        if "youtube.com" in url or "youtu.be" in url:
            import re
            m = re.search(r"v=([a-zA-Z0-9_-]+)", url) or re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
            return m.group(1) if m else url[:40]
        return url[:50] + "..." if len(url) > 50 else url
    except Exception:
        return url[:40]
