[app]
title = Quiz AI
package.name = quizai
package.domain = org.kata.quizai

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt

version = 1.0.0
android.version_code = 1

# ✅ SINGLE LINE (VERY IMPORTANT)
requirements = python3,kivy==2.2.1,requests==2.31.0,pyjnius==1.4.2,cython<3.0,setuptools<70,wheel

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# ✅ REQUIRED
android.ndk = 25b
p4a.branch = develop
p4a.build_tool = gradle

android.gradle = True
android.enable_androidx = True

android.aab = False
android.build_mode = release

android.accept_sdk_license = True
android.permissions = INTERNET

log_level = 2
icon.filename = assets/icon.png

exclude_patterns = tests,docs,*.md,.gitignore,.github
warn_on_root = 1
