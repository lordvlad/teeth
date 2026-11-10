# Zahnputz-Timer Android App

A minimal, full-screen WebView app shell following the Gradle-free design from `../valet`.

## Highlights
- **No Android Studio / No Gradle**: Built in seconds using standard CLI tools (`aapt2`, `javac`, `d8` via `r8.jar`, `zipalign`, `apksigner`).
- **100% Offline & Self-Contained**: `index.html` is packaged directly into the APK under `assets/index.html` (`file:///android_asset/index.html`). No dev server or local network required.
- **Native Screen Wake Lock & Vibration**: Exposes an `AndroidBridge` Javascript interface to native Android window flags (`FLAG_KEEP_SCREEN_ON`) and `Vibrator`.
- **Tiny footprint**: ~21 KB total APK size.

## Build
```bash
cd android
bun run build.ts
```
Output: `android/build/teeth.apk`.

## Install
Connect an Android device with USB debugging enabled:
```bash
/data/android-sdk/platform-tools/adb install -r android/build/teeth.apk
```
Or transfer `teeth.apk` directly to the phone/tablet and install via file manager.
