[app]

# (str) Title of your application
# (str) Package name
# (str) Package domain (needed for android/ios packaging)
title = QuizAI Academy
package.name = quizaiacademy
package.domain = com.quizai

# (str) Source code where the main.py lives
source.dir = mobile_app

# (list) Source files to include (let Buildozer include everything in source.dir)
source.include_exts = py,png,jpg,jpeg,kv

# (list) Application requirements
requirements = python3,kivy

# (str) Entry point
entrypoint = main.py

# (str) Minimum API target
android.minapi = 21

# (str) Target API
android.api = 33

# (str) Android SDK path
android.sdk_path = /opt/android-sdk

# (bool) Accept SDK licenses automatically
android.accept_sdk_license = True

# (str) Python-for-android version pin
p4a.branch = 2023.09.16

# (str) Cython version pin
cython = 0.29.36

# (str) Android build tools version
android.build_tools_version = 33.0.2

# (list) Permissions
android.permissions = INTERNET

# (bool) Enable logcat
android.logcat_filter = *:S python:D
=======
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
>>>>>>> main

[buildozer]
log_level = 2
warn_on_root = 0
