[app]

# =========================
# App Info
# =========================
title = Quiz AI
package.name = quizai
package.domain = org.kata.quizai

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
# UI
# =========================
orientation = portrait
fullscreen = 0

# =========================
# Android CONFIG (CRITICAL)
# =========================
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.ndk = 25.2.9519653
android.ndk_api = 21

# 🔥 FORCE GRADLE (FIXES YOUR ERROR)
android.gradle = True
android.enable_androidx = True

# 🔥 DISABLE ANT COMPLETELY
android.ant_path =

# SDK handling
android.sdk_path = $ANDROID_SDK_ROOT
android.accept_sdk_license = True

# =========================
# Permissions
# =========================
android.permissions = INTERNET

# =========================
# Logging
# =========================
log_level = 2

# =========================
# Cleanup
# =========================
exclude_patterns = tests,docs,*.md,.gitignore,.github

warn_on_root = 1
