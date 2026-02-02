[app]
title = Quiz AI App
package.name = quizai
package.domain = org.kranthu

source.dir = .
source.include_exts = py,png,jpg,kv

version = 0.1

requirements = python3,kivy
bootstrap = sdl2

orientation = portrait
fullscreen = 1

# ---------------- Android ----------------

android.api = 33
android.minapi = 21
android.ndk = 25b

# IMPORTANT: single architecture only
android.arch = arm64-v8a

android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = False

# ---------------- Buildozer ----------------

[buildozer]
log_level = 2
warn_on_root = 1
