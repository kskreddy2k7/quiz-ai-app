[app]
title = Quiz AI App
package.name = quizai
package.domain = org.kranthu

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ini

version = 0.1

requirements = python3,kivy,pymupdf,python-docx,python-pptx

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE

# ---- ANDROID CONFIG (CRITICAL) ----
android.api = 33
android.minapi = 21
android.build_tools = 33.0.2

# ---- FORCE SUPPORTED NDK (FIXES CRASH) ----
android.ndk = 25b
android.ndk_api = 21

# ---- USE ONE ARCH (STABLE IN CI) ----
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
