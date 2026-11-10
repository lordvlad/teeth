#!/usr/bin/env bun
// Lightweight Android APK build without Android Studio / Gradle:
// aapt2 + javac + d8 (r8.jar) + zip + zipalign + apksigner
import { $ } from "bun";
import { rm, mkdir } from "node:fs/promises";

process.chdir(import.meta.dir);
$.throws(true);

const sdk = process.env.ANDROID_HOME ?? "/data/android-sdk";
const bt = `${sdk}/build-tools/34.0.0`;
const jar = `${sdk}/platforms/android-34/android.jar`;
const ks = process.env.TEETH_KEYSTORE ?? `${import.meta.dir}/teeth-debug.keystore`;

console.log("Cleaning build directory...");
await rm("build", { recursive: true, force: true });
await mkdir("build/classes", { recursive: true });
await mkdir("assets", { recursive: true });

// Always keep assets/index.html in sync with parent index.html
await $`cp ../public/index.html assets/index.html`;

console.log("Compiling Android resources...");
await $`${bt}/aapt2 compile --dir res -o build/res.zip`;

console.log("Linking APK with manifest and assets...");
await $`${bt}/aapt2 link -I ${jar} --manifest AndroidManifest.xml -A assets --min-sdk-version 26 --target-sdk-version 34 --version-code 1 --version-name 1.0 -o build/base.apk build/res.zip --java build/gen`;

console.log("Compiling Java sources...");
await $`javac --release 11 -g -cp ${jar} -d build/classes src/app/teeth/*.java build/gen/app/teeth/R.java`;

console.log("Dexing with D8...");
// The build-tools d8 crashes on very new JDKs, so prefer the standalone R8 jar when present; otherwise use d8 (JDK 17 on CI).
const classes = (await Array.fromAsync(new Bun.Glob("app/teeth/*.class").scan({ cwd: "build/classes" }))).map(f => `build/classes/${f}`);
if (await Bun.file(`${sdk}/r8.jar`).exists()) {
  await $`java -cp ${sdk}/r8.jar com.android.tools.r8.D8 --release --min-api 26 --lib ${jar} --output build ${classes}`;
} else {
  await $`${bt}/d8 --release --min-api 26 --lib ${jar} --output build ${classes}`;
}

console.log("Packaging DEX into APK...");
await $`cp build/base.apk build/unsigned.apk`;
await $`zip -qj build/unsigned.apk build/classes.dex`;

console.log("Aligning APK...");
await $`${bt}/zipalign -f 4 build/unsigned.apk build/aligned.apk`;

if (!(await Bun.file(ks).exists())) {
  console.log("Generating debug keystore...");
  await $`keytool -genkeypair -keystore ${ks} -storepass android -keypass android -alias teeth -dname CN=teeth -keyalg RSA -keysize 2048 -validity 10000`.quiet();
}

console.log("Signing APK...");
await $`${bt}/apksigner sign --ks ${ks} --ks-pass pass:android --out build/teeth.apk build/aligned.apk`.quiet();
await $`cp build/teeth.apk ../public/teeth.apk`;

const apk = Bun.file("build/teeth.apk");
console.log(`Success! Built build/teeth.apk (${(apk.size / 1024).toFixed(1)} KB)`);
