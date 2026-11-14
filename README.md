# Zahnputz-Timer

Kids' tooth brushing timer: single-page, offline-first PWA (`public/`) plus a WebView Android app (`android/`). Built from the `pwa-pages-publish` skill template (server, service worker, Android shell and Pages workflow follow it; the timer UI, the NoSleep video fallback in `setAwake()` and the landscape layout are app-specific).

- **Run:** `bun src/server.ts` (`PORT`, default 8790), serves `public/` only, always `no-cache`.
- **Offline:** `public/sw.js` precaches `ASSETS` (add new files there). CI stamps `BUILD` with the commit hash so every deploy gets a fresh cache; bump it by hand only when testing locally.
- **Android:** `bun run android` wraps `public/` in a WebView app (no Gradle; SDK at `$ANDROID_HOME`, default `/data/android-sdk`) and writes `public/teeth.apk`. Signing key `android/teeth-debug.keystore` (alias `teeth`, password `android`, gitignored; override with `APP_KEYSTORE`). `APP_VERSION_CODE` sets the versionCode (CI: run number). Inside the app `window.AndroidBridge` keeps the screen on while the timer runs (`FLAG_KEEP_SCREEN_ON`), vibrates and opens PayPal.
- **Donate:** heart bottom right behind a maths gate; browsers load the PayPal SDK (HTTPS / service worker only), the APK opens the hosted PayPal page in the system browser. Heart and download icon hide while the timer is not idle.
- **Download:** the icon bottom left appears when `teeth.apk` is reachable (browser only).

## Publish

Push to `main`; `.github/workflows/pages.yml` builds the APK and deploys `public/` to https://lordvlad.github.io/teeth/ (repo Settings > Pages > Source: GitHub Actions). CI signs the APK with the secret `ANDROID_KEYSTORE_B64` (`base64 -w0 android/teeth-debug.keystore`); without it every build gets a throwaway key and can't update an installed copy.

## Homelab

systemd user unit `~/.config/systemd/user/teeth.service` (`PORT=8791`), published as Tailscale Service `svc:teeth` -> https://teeth.anchovy-crocodile.ts.net/ via `tailscale serve --service=svc:teeth --https=443 --bg http://127.0.0.1:8791`. Static files need no restart.
