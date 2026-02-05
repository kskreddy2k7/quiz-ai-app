[app]

# (str) Title of your application
title = Quiz AI

# (str) Package name
package.name = quizai

# (str) Package domain (needed for android packaging)
package.domain = org.kata.quizai

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,json,txt

# (str) Application versioning (method 1)
version = 1.0.0

# (int) Android version code
android.version_code = 1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.1,requests==2.31.0,openai>=1.12.0,httpx>=0.27.0,pyjnius==1.4.2,cython<3.0,setuptools<70,wheel,pypdf>=3.17.0,python-docx>=1.1.0,lxml,openssl

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (str) python-for-android branch to use, defaults to master
p4a.branch = develop

# (bool) Use the new gradle build system
android.gradle = True

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Whether to build a bundle (AAB) or an APK
android.aab = False

# (str) The build mode (debug or release)
android.build_mode = debug

# (bool) Accept SDK license
android.accept_sdk_license = True

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Log level (0 = error only, 1 = info, 2 = debug (with p4a output))
log_level = 2

# (str) Custom source for any requirement
# p4a.local_recipes = ./recipes

# (str) Filename to the icon of the application
icon.filename = assets/icon.png

# (list) List of patterns to exclude
exclude_patterns = tests,docs,*.md,.gitignore,.github

# (bool) warn on root building
warn_on_root = 1
