[app]
# -------- App Identity --------
title = S Quiz
package.name = squiz
package.domain = org.kranthu

# -------- Source --------
source.dir = .
source.include_exts = py,png,jpg,kv,json

# -------- Versioning --------
version = 1.0

# -------- Requirements --------
requirements = python3,kivy,pymupdf,python-docx,python-pptx,requests
bootstrap = sdl2

# -------- Display --------
orientation = portrait
fullscreen = 1

# -------- Android SDK / NDK --------
android.api = 33
android.minapi = 21

# ⚠️ IMPORTANT: Use STABLE NDK (25c recommended)
android.ndk = 25c

# -------- Architectures --------
android.arch = arm64-v8a

# -------- Permissions --------
android.permissions = INTERNET

# -------- Android Settings --------
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = False

# -------- Performance --------
android.logcat_filters = *:S python:D
android.debuggable = False


[buildozer]
log_level = 2
warn_on_root = 1
