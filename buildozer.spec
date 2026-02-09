[app]
title = Smile - Download Manager
package.name = smile_downloader
package.domain = org.smile

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,wav,txt

version = 2.0.1

requirements = python3,kivy,pillow,yt-dlp,requests,certifi

permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.features = android.hardware.usb.host

android.api = 31
android.minapi = 21
android.ndk = 25b

android.gradle_dependencies = 

android.add_src = 

[buildozer]
log_level = 2
warn_on_root = 1
