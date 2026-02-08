[app]

# (str) Title of your application
title = S Quiz

# (str) Package name
package.name = squiz

# (str) Package domain (needed for android/ios packaging)
package.domain = com.sai

# (str) Source code where the main.py live
source.dir = .

# Use develop branch for stable releases (master is deprecated)
p4a.branch = develop

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,html,js,css,json,svg

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,pyjnius

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
# Using API 34 to match installed Android platform
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# Using NDK 25b for better compatibility
android.ndk = 25b

# (str) Android build-tools version to use
# Using build-tools 36.0.0 for compatibility with latest Android SDK
android.build_tools_version = 36.0.0

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (str) Path to the icon (if not provided, default icon is used)
icon.filename = static/app-icon.svg

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Presplash background color (for new android toolchain)
android.presplash_color = #6366f1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (bool) Automatic accept of the SDK license
android.accept_sdk_license = True

