[app]
title = Quiz AI App
package.name = quizai
package.domain = org.kranthu

source.dir = .
source.include_exts = py,kv

version = 0.1

requirements = python3,kivy
bootstrap = sdl2

orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a

android.permissions = MANAGE_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
