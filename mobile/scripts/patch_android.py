#!/usr/bin/env python3
"""Customises the Android project that `npx cap add android` generated (run from mobile/)."""
import glob
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOBILE = os.path.dirname(HERE)
APP = os.path.join(MOBILE, "android", "app")
RES = os.path.join(APP, "src", "main", "res")
MANIFEST = os.path.join(APP, "src", "main", "AndroidManifest.xml")
ASSETS = os.path.join(MOBILE, "res")


def log(message):
    print("[patch_android] " + message)


# 1. Manifest: "Open with PdfCraft" for PDFs, no cloud backup of documents, room for big files.
with open(MANIFEST, encoding="utf-8") as f:
    manifest = f.read()

PDF_FILTER = """
            <!-- "Open with PdfCraft" from file managers, mail, browsers... -->
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="content" android:mimeType="application/pdf" />
                <data android:scheme="file" android:mimeType="application/pdf" />
            </intent-filter>
"""
if "application/pdf" not in manifest:
    if "</activity>" not in manifest:
        sys.exit("[patch_android] no </activity> in the manifest: the Capacitor template changed")
    manifest = manifest.replace("</activity>", PDF_FILTER + "        </activity>", 1)
manifest = manifest.replace('android:allowBackup="true"', 'android:allowBackup="false"')
if "android:largeHeap" not in manifest:
    manifest = manifest.replace("<application", '<application\n        android:largeHeap="true"', 1)
if "android:windowSoftInputMode" not in manifest:
    manifest = manifest.replace("<activity", '<activity\n            android:windowSoftInputMode="adjustResize"', 1)
with open(MANIFEST, "w", encoding="utf-8") as f:
    f.write(manifest)
log("manifest patched")

# 2. Release signing + version (see signing.gradle).
shutil.copy(os.path.join(HERE, "signing.gradle"), os.path.join(APP, "signing.gradle"))
for name, line in (("build.gradle", "\napply from: 'signing.gradle'\n"), ("build.gradle.kts", '\napply(from = "signing.gradle")\n')):
    path = os.path.join(APP, name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if "signing.gradle" not in text:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
        log("signing hooked into " + name)
        break
else:
    sys.exit("[patch_android] no android/app/build.gradle found")

# 3. Icons and splash (cosmetic: a problem here never fails the build).
try:
    for density in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
        folder = os.path.join(RES, "mipmap-" + density)
        os.makedirs(folder, exist_ok=True)
        for old in glob.glob(os.path.join(folder, "ic_launcher*.webp")):
            os.remove(old)
        for name in ("ic_launcher.png", "ic_launcher_round.png"):
            source = os.path.join(ASSETS, "mipmap-" + density, name)
            if os.path.exists(source):
                shutil.copy(source, folder)
    # The adaptive icon would hide the plain PNGs on Android 8+.
    shutil.rmtree(os.path.join(RES, "mipmap-anydpi-v26"), ignore_errors=True)
    splash = os.path.join(ASSETS, "splash.png")
    for target in glob.glob(os.path.join(RES, "drawable*", "splash.png")):
        shutil.copy(splash, target)
    log("icons and splash replaced")
except Exception as error:  # noqa: BLE001
    log("icons skipped: %s" % error)
