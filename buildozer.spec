[app]
title = S Quiz
package.name = squizbysai
package.domain = org.sai.squiz
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
version = 1.0.0

# Core requirements (Removed google-generativeai because it won't compile for Android)
requirements = python3,kivy==2.2.1,requests,pyjnius,certifi,openssl

orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Permissions required for AI and storage
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# UI and Assets
icon.filename = assets/icon.png
# presplash.filename = assets/presplash.png

# Build settings
p4a.branch = master
android.gradle_dependencies = 
android.enable_androidx = True
android.accept_sdk_license = True
android.skip_update = False
android.no_byte_compile_python = False

[buildozer]
log_level = 2
warn_on_root = 1
