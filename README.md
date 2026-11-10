# Zahnputz-Timer

Kids' tooth brushing timer: single-page offline-first PWA (`public/`) plus a WebView Android app (`android/`).

- **Run:** `bun src/server.ts` (`PORT`, default 8791). Serves `public/` only.
- **Deploy:** systemd user unit `~/.config/systemd/user/teeth.service` (port 8791), published as Tailscale Service `svc:teeth` -> https://teeth.anchovy-crocodile.ts.net/ via `tailscale serve --service=svc:teeth --https=443 --bg http://127.0.0.1:8791`. Static files need no restart; bump `CACHE` in `public/sw.js` on changes.
- **Android:** `bun run android` copies `public/index.html` into the APK and writes `public/teeth.apk` (served as the browser-only download link). Needs the SDK at `/data/android-sdk`.
- **Donate:** heart bottom right behind a maths gate; browser uses the PayPal SDK (HTTPS/service worker only), the APK opens the hosted PayPal page in the system browser.

## GitHub Pages

`.github/workflows/pages.yml` builds the APK and publishes `public/` to https://lordvlad.github.io/teeth/ on every push to `main` (the donate heart and the APK download link both work there, since it is HTTPS).

- One-time: repo Settings > Pages > Source = **GitHub Actions**.
- Optional: add secret `ANDROID_KEYSTORE_B64` (`base64 -w0 android/teeth-debug.keystore`) so CI signs the APK with the same key as local builds; otherwise each build uses a throwaway key and can't update an installed copy.
- `public/teeth.apk`, `android/build/` and keystores are not committed.
