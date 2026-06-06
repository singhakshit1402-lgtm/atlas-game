[app]
# (str) Title of your application
title = Atlas Game

# (str) Package name
package.name = com.atlasgamebyAk

# (str) Package domain (needed for android packaging)
package.domain = org.example

# (str) Source code where the main.py lives
source.dir = .

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

presplash.filename = %(source.dir)s/presplash.png

# (list) Source files to include (matches all your uploaded assets)
source.include_exts = py,png,jpg,kv,wav,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements 
requirements = python3,kivy,requests,plyer,certifi,urllib3

# (list) Supported orientations
orientation = portrait

# (bool) Use fullscreen mode
fullscreen = 1
# Ensure the line is uncommented (remove any '#' symbol at the front)
android.permissions = android.permission.INTERNET, android.permission.ACCESS_NETWORK_STATE

# ==========================================
# Android specific configuration
# ==========================================

# (int) Target Android API (API 33 is required for modern compilers)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK architecture (Builds for modern phones)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Skip byte-compilation for .py files if compilation fails
android.skip_byte_compile = 1

# (str) Format used to package the app
android.release_artifact = apk

# (bool) Automatically accept SDK/NDK licenses on GitHub virtual runner
android.accept_apk_license = True

[buildozer]
# (int) Log level (2 = standard details, 1 = error only)
log_level = 2

# (int) Display warning animations
warn_on_root = 1
