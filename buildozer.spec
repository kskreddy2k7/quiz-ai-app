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
version = 1.0.0
android.version_code = 100

# =========================
# Python Requirements (ANDROID SAFE)
# =========================
requirements = python3,kivy,requests,openai==1.3.7

# =========================
# UI
# =========================
orientation = portrait
fullscreen = 0

# =========================
# Android (STABLE CONFIG)
# =========================
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# 🔥 FORCE GRADLE (CRITICAL)
p4a.build_tool = gradle
android.gradle = True
android.enable_androidx = True
android.aab = True

# 🔥 HARD DISABLE ANT (CRITICAL)
android.ant_path =
android.ant =
android.ant_bin =

# Accept licenses automatically (CI safe)
android.accept_sdk_license = True

# =========================
# Permissions (MINIMUM)
# =========================
android.permissions = INTERNET

# =========================
# Logging
# =========================
log_level = 2

# =========================
# Assets
# =========================
icon.filename = assets/icon.png

# =========================
# Cleanup
# =========================
exclude_patterns = tests,docs,*.md,.gitignore,.github

warn_on_root = 1
