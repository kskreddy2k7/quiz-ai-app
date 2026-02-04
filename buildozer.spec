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
android.version_code = 1

# =========================
# Python Requirements (PINNED)
# =========================
requirements = python3==3.10,kivy==2.2.1,requests==2.31.0,openai==1.3.7,pyjnius==1.4.2,cython==0.29.36

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
android.ndk_version = 25.2.9519653

# 🔥 FORCE python-for-android stable branch
p4a.branch = stable
p4a.version = 2023.10.01

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
