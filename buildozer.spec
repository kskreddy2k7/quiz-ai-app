[app]
title = S Quiz
package.name = squiz
package.domain = org.kranthu
version = 1.0
source.dir = .
source.include_exts = py,png,jpg,json

requirements = python3,kivy,pymupdf,python-docx,python-pptx
orientation = portrait
fullscreen = 1

icon.filename = assets/icon.png

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25c
android.arch = arm64-v8a
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1
