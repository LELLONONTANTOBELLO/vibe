[app]
title = Vibration Controller
package.name = vibecontroller
package.domain = it.crashando

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy==2.3.0,plyer,requests,certifi,urllib3,charset-normalizer,idna

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,VIBRATE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.arch = arm64-v8a

p4a.branch = main

[buildozer]
log_level = 2
warn_on_root = 0