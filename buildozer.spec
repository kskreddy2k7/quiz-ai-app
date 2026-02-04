[app]
title = Quiz AI
package.name = quizai
package.domain = org.kata.quizai

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt

version = 1.0.0
android.version_code = 1

# ✅ SAFE REQUIREMENTS
requirements = python3,kivy==2.2.1,requests==2.31.0,openai==1.3.7,pyjnius==1.5.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# ✅ python-for-android (STABLE)
p4a.branch = stable
p4a.build_tool = gradle

android.gradle = True
android.enable_androidx = True

# 🔒 FORCE APK ONLY (NO AAB)
android.aab = False
android.build_mode = debug

# ❌ ANT DISABLED
android.ant_path =
android.ant =
android.ant_bin =

android.accept_sdk_license = True

android.permissions = INTERNET

log_level = 2

icon.filename = assets/icon.png

exclude_patterns = tests,docs,*.md,.gitignore,.github
warn_on_root = 1
