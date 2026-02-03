[app]

# =========================
# App basic information
# =========================
title = Quiz AI
package.name = quizai
package.domain = org.example

# =========================
# Source
# =========================
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt

# =========================
# Version
# =========================
version = 0.1

# =========================
# Requirements
# =========================
requirements = python3,kivy

# =========================
# Orientation & UI
# =========================
orientation = portrait
fullscreen = 0

# =========================
# Android specific
# =========================
android.api = 33
android.minapi = 21
android.sdk_path = $ANDROID_SDK_ROOT
android.accept_sdk_license = True

# Use stable build tools
android.build_tools_version = 33.0.2

# =========================
# Permissions (add later if needed)
# =========================
android.permissions = INTERNET

# =========================
# Logging
# =========================
log_level = 2

# =========================
# Exclude unnecessary files
# =========================
exclude_patterns = tests,docs,*.md,.gitignore,.github

# =========================
# Build options
# =========================
warn_on_root = 1
