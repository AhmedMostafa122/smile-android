"""
Multimedia Download Engine
Supports streaming platforms (YouTube, etc.) and direct file downloads.
Enhanced with complete format support and performance optimizations.
"""

import os
import yt_dlp
import requests
from urllib.parse import urlparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


# Supported streaming domains for yt-dlp
STREAMING_DOMAINS = (
    "youtube.com", "youtu.be", "vimeo.com", "dailymotion.com",
    "twitch.tv", "twitter.com", "x.com", "facebook.com", "fb.watch",
    "instagram.com", "tiktok.com", "soundcloud.com", "bandcamp.com",
    "reddit.com", "rumble.com", "odysee.com", "kick.com", "spotify.com",
    "ted.com", "bbc.co.uk", "bbc.com", "4chan.org", "mastodon.social",
    "pixiv.net", "patreon.com", "pornhub.com", "twitch.tv"
)

# Comprehensive Video Format Support
VIDEO_FORMATS = {
    # Container formats
    "MP4": "bestvideo+bestaudio/best[ext=mp4]",
    "WebM": "bestvideo[ext=webm]+bestaudio[ext=webm]/best",
    "MKV": "bestvideo+bestaudio/best[ext=mkv]",
    "MOV": "bestvideo+bestaudio/best[ext=mov]",
    "AVI": "bestvideo+bestaudio/best[ext=avi]",
    "FLV": "bestvideo+bestaudio/best[ext=flv]",
    "3GP": "bestvideo+bestaudio/best[ext=3gp]",
    "TSV": "bestvideo+bestaudio/best[ext=ts]",
    "M4V": "bestvideo[ext=m4v]+bestaudio[ext=m4a]/best",
    "ASF": "bestvideo+bestaudio/best[ext=asf]",
    "WMV": "bestvideo+bestaudio/best[ext=wmv]",
    "VOB": "bestvideo+bestaudio/best[ext=vob]",
    "OGV": "bestvideo[ext=ogv]+bestaudio[ext=ogg]/best",
    "MPEG": "bestvideo+bestaudio/best[ext=mpeg]",
    "MPG": "bestvideo+bestaudio/best[ext=mpg]",
    "HEVC": "bestvideo[vcodec=hevc]+bestaudio[acodec=aac]/best",
    "H264": "bestvideo[vcodec=h264]+bestaudio[acodec=aac]/best",
    "VP8": "bestvideo[vcodec=vp8]+bestaudio/best",
    "VP9": "bestvideo[vcodec=vp9]+bestaudio[acodec=opus]/best",
    "AV1": "bestvideo[vcodec=av01]+bestaudio/best",
}

# Comprehensive Audio Format Support
AUDIO_FORMATS = {
    # Lossy formats
    "MP3": {"codec": "mp3", "quality": "320"},
    "M4A": {"codec": "m4a", "quality": "320"},
    "AAC": {"codec": "aac", "quality": "320"},
    "OGG": {"codec": "vorbis", "quality": "320"},
    "OPUS": {"codec": "opus", "quality": "160"},
    "VBR MP3": {"codec": "mp3", "quality": "vbr"},
    "WMA": {"codec": "wma", "quality": "192"},
    "AC3": {"codec": "ac3", "quality": "192"},
    "DTS": {"codec": "dts", "quality": "192"},
    
    # Lossless formats
    "FLAC": {"codec": "flac", "quality": "192"},
    "WAV": {"codec": "wav", "quality": "192"},
    "ALAC": {"codec": "alac", "quality": "192"},
    "LOSSLESS": {"codec": "flac", "quality": "192"},
    "APE": {"codec": "ape", "quality": "192"},
    
    # Speech/Misc formats
    "SPEECH": {"codec": "libmp3lame", "quality": "128"},
    "VOICE": {"codec": "libmp3lame", "quality": "96"},
    "LOW": {"codec": "mp3", "quality": "128"},
    "MEDIUM": {"codec": "mp3", "quality": "192"},
    "HIGH": {"codec": "mp3", "quality": "256"},
    "ULTRA": {"codec": "flac", "quality": "192"},
}

# Format to file extension mapping
FORMAT_EXTENSIONS = {
    # Video
    "MP4": "mp4", "WebM": "webm", "MKV": "mkv", "MOV": "mov",
    "AVI": "avi", "FLV": "flv", "3GP": "3gp", "TSV": "ts",
    "M4V": "m4v", "ASF": "asf", "WMV": "wmv", "VOB": "vob",
    "OGV": "ogv", "MPEG": "mpeg", "MPG": "mpg", "HEVC": "mp4",
    "H264": "mp4", "VP8": "webm", "VP9": "webm", "AV1": "webm",
    # Audio
    "MP3": "mp3", "M4A": "m4a", "AAC": "aac", "FLAC": "flac",
    "WAV": "wav", "OPUS": "opus", "OGG": "ogg", "WMA": "wma",
    "AC3": "ac3", "DTS": "dts", "ALAC": "alac", "APE": "ape",
    "VBR MP3": "mp3", "SPEECH": "mp3", "VOICE": "mp3",
    "LOW": "mp3", "MEDIUM": "mp3", "HIGH": "mp3", "ULTRA": "flac",
    "LOSSLESS": "flac",
}


def is_streaming_url(url: str) -> bool:
    """Check if URL is from a supported streaming platform."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(d in domain for d in STREAMING_DOMAINS)
    except Exception:
        return False


def download_streaming(url: str, download_path: str, quality: str, media_format: str, progress_hook=None) -> bool:
    """Download from YouTube and other streaming platforms using yt-dlp with optimizations."""
    if media_format in VIDEO_FORMATS:
        outtmpl = os.path.join(download_path, "%(title)s_%(height)sp.%(ext)s")
    else:
        outtmpl = os.path.join(download_path, "%(title)s_AUDIO.%(ext)s")

    # Optimized yt-dlp configuration for faster downloads
    ydl_opts = {
        "outtmpl": outtmpl,
        "ignoreerrors": True,
        "noplaylist": False,
        "overwrites": False,
        "concurrent_fragment_downloads": 32,  # Increased for parallel fragment downloads
        "socket_timeout": 30,
        "retries": 5,
        "retry_sleep": 2,
        "http_chunk_size": 2097152,  # 2MB chunks for optimal transfer speed
        "bidi_workaround": False,
        "quiet": False,
        "no_warnings": False,
        "extract_flat": False,
        "allow_unplayable_formats": True,
        "prefer_insecure": False,
        "youtube_include_dash_manifest": True,
        "trim_file_name": 200,
    }

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    if media_format in VIDEO_FORMATS:
        if quality == "Best":
            ydl_opts["format"] = VIDEO_FORMATS.get(media_format, "bestvideo+bestaudio/best")
        else:
            height = quality.replace("p", "")
            ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best"
        
        # Set merge format based on selected format
        merge_formats = {
            "WebM": "webm", "MKV": "mkv", "MOV": "mov", "AVI": "avi",
            "FLV": "flv", "3GP": "3gp", "TSV": "ts", "M4V": "m4v",
            "ASF": "asf", "WMV": "wmv", "VOB": "vob", "OGV": "ogv",
            "MPEG": "mpeg", "MPG": "mpg", "HEVC": "mp4", "H264": "mp4",
        }
        ydl_opts["merge_output_format"] = merge_formats.get(media_format, "mp4")
    else:
        ydl_opts["format"] = "bestaudio/best"
        format_config = AUDIO_FORMATS.get(media_format, AUDIO_FORMATS["MP3"])
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": format_config["codec"],
            "preferredquality": format_config["quality"]
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        if progress_hook:
            progress_hook({"status": "error", "error": str(e)})
        return False


def download_direct(url: str, download_path: str, progress_hook=None) -> bool:
    """Download direct file (images, PDFs, etc.) via HTTP with parallel optimization."""
    try:
        # Create session with connection pooling for faster downloads
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()

        filename = os.path.basename(urlparse(url).path)
        if not filename or "." not in filename:
            filename = f"download_{hash(url) % 10000}"

        filepath = os.path.join(download_path, filename)
        total_size = int(response.headers.get("content-length", 0))
        
        # Use larger chunks for faster transfer
        downloaded = 0
        chunk_size = 4194304  # 4MB chunks for optimal speed
        start_time = os.times()[4] if hasattr(os, 'times') else 0
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_hook and total_size:
                        pct = min(100, (downloaded / total_size) * 100)
                        elapsed = (os.times()[4] if hasattr(os, 'times') else 0) - start_time
                        speed_mbps = (downloaded / (1024 * 1024)) / max(elapsed, 0.1)
                        progress_hook({
                            "status": "downloading",
                            "_percent_str": f"{pct:.1f}%",
                            "_speed_str": f"{speed_mbps:.2f} MB/s"
                        })

        if progress_hook:
            progress_hook({"status": "finished"})
        session.close()
        return True
    except Exception as e:
        if progress_hook:
            progress_hook({"status": "error", "error": str(e)})
        return False


def download(url: str, download_path: str, quality: str = "Best", media_format: str = "Video", progress_hook=None) -> bool:
    """Unified download entry point - auto-detects source type."""
    if is_streaming_url(url):
        return download_streaming(url, download_path, quality, media_format, progress_hook)
    return download_direct(url, download_path, progress_hook)
