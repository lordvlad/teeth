#!/usr/bin/env bun
// Gradle-free Android build: aapt2 + javac + d8 + zip + zipalign + apksigner. Output: public/teeth.apk
// Needs an Android SDK at $ANDROID_HOME (default /data/android-sdk): platforms/android-34 and build-tools/34.0.0.
// Env: APP_KEYSTORE (signing key, default android/teeth-debug.keystore, created if missing), APP_VERSION_CODE (default 1).
import { $ } from "bun";
import { rm, mkdir, cp } from "node:fs/promises";

process.chdir(import.meta.dir);
$.throws(true);

const sdk = process.env.ANDROID_HOME ?? "/data/android-sdk";
const bt = `${sdk}/build-tools/34.0.0`;
const jar = `${sdk}/platforms/android-34/android.jar`;
const ks = process.env.APP_KEYSTORE ?? `${import.meta.dir}/teeth-debug.keystore`;
const version = process.env.APP_VERSION_CODE ?? "1";

console.log("Cleaning build directory...");
await rm("build", { recursive: true, force: true });
await rm("assets", { recursive: true, force: true });
await mkdir("build/classes", { recursive: true });

// Bundle the web app. sw.js, the APK itself and docs are left out: the WebView serves the assets directly.
await cp("../public", "assets", { recursive: true, filter: src => !/(sw\.js|\.apk|\.md)$/.test(src) });

console.log("Compiling Android resources...");
await $`${bt}/aapt2 compile --dir res -o build/res.zip`;

console.log("Linking APK with manifest and assets...");
await $`${bt}/aapt2 link -I ${jar} --manifest AndroidManifest.xml -A assets --min-sdk-version 26 --target-sdk-version 34 --version-code ${version} --version-name 1.${version} -o build/base.apk build/res.zip --java build/gen`;

console.log("Compiling Java sources...");
await $`javac --release 11 -g -cp ${jar} -d build/classes src/app/teeth/MainActivity.java build/gen/app/teeth/R.java`;

console.log("Dexing...");
// The build-tools d8 crashes on very new JDKs, so prefer the standalone R8 jar when present; otherwise use d8 (JDK 17 on CI).
const classes = (await Array.fromAsync(new Bun.Glob("app/teeth/*.class").scan({ cwd: "build/classes" }))).map(f => `build/classes/${f}`);
if (await Bun.file(`${sdk}/r8.jar`).exists()) {
  await $`java -cp ${sdk}/r8.jar com.android.tools.r8.D8 --release --min-api 26 --lib ${jar} --output build ${classes}`;
} else {
  await $`${bt}/d8 --release --min-api 26 --lib ${jar} --output build ${classes}`;
}

console.log("Packaging, aligning, signing...");
await $`cp build/base.apk build/unsigned.apk`;
await $`zip -qj build/unsigned.apk build/classes.dex`;
await $`${bt}/zipalign -f 4 build/unsigned.apk build/aligned.apk`;

if (!(await Bun.file(ks).exists())) {
  console.log("Generating debug keystore (keep it: updates must be signed with the same key)...");
  await $`keytool -genkeypair -keystore ${ks} -storepass android -keypass android -alias teeth -dname CN=teeth -keyalg RSA -keysize 2048 -validity 10000`.quiet();
}
await $`${bt}/apksigner sign --ks ${ks} --ks-pass pass:android --out build/teeth.apk build/aligned.apk`.quiet();
await $`cp build/teeth.apk ../public/teeth.apk`;

const apk = Bun.file("build/teeth.apk");
console.log(`Success! public/teeth.apk ${(apk.size / 1024).toFixed(1)} KB, versionCode ${version}`);
