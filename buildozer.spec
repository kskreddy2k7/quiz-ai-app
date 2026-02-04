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
# Requirements (SAFE)
# =========================
requirements = python3,kivy,requests,python-dotenv,openai

# =========================
# UI
# =========================
orientation = portrait
fullscreen = 0

# =========================
# Android CONFIG (DO NOT FORCE)
# =========================
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

android.gradle = True
android.enable_androidx = True
android.ant_path =

android.accept_sdk_license = True

# =========================
# Permissions (MINIMAL)
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
