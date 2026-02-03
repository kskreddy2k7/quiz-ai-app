[app]
# -----------------------------
# App identity
# -----------------------------
title = S Quiz
package.name = squiz
package.domain = org.kranthu

# -----------------------------
# Source
# -----------------------------
source.dir = .
source.include_exts = py,png,jpg,kv,json

# -----------------------------
# Version
# -----------------------------
version = 1.0

# -----------------------------
# Requirements
# -----------------------------
requirements = python3,kivy,pymupdf,python-docx,python-pptx
bootstrap = sdl2

# -----------------------------
# App icon (IMPORTANT)
# -----------------------------
icon.filename = assets/icon.png

# -----------------------------
# Orientation & display
# -----------------------------
orientation = portrait
fullscreen = 1

# -----------------------------
# Android API levels
# -----------------------------
android.api = 33
android.minapi = 21

# -----------------------------
# NDK (STABLE)
# -----------------------------
android.ndk = 25c

# -----------------------------
# Architecture
# -----------------------------
android.arch = arm64-v8a

# -----------------------------
# Permissions (REQUIRED for file upload)
# -----------------------------
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# -----------------------------
# Android settings
# -----------------------------
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = False

# -----------------------------
# Logging (reduce noise)
# -----------------------------
android.logcat_filters = *:S python:D
android.debuggable = False


[buildozer]
log_level = 2
warn_on_root = 1
