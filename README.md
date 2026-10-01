# عدّاد الصلاة — Salah Counter

Offline Android app that counts ركعات and سجدات by touch, announces التشهد,
and tells you which prayer you just finished.

## Getting the APK without installing Android Studio

1. Create a new GitHub repo and push these files to the `main` branch.
2. Open the **Actions** tab. The **Build APK** workflow starts on its own
   (or run it manually with *Run workflow*).
3. When it turns green — about 4–6 minutes — open the run and download the
   **salah-counter-apk** artifact. Unzip it to get `app-debug.apk`.
4. Copy the APK to your phone, tap it, and allow "install unknown apps" for
   whichever app you opened it from.

The APK is signed with Android's standard debug key, which is fine for
installing on your own device. You only need a real signing key to publish
on Google Play.

## Changing the app

Everything lives in `www/index.html` — one file, no build step. Edit it,
push, and the workflow produces a new APK. The version Android shows in
Settings comes from `version` in `package.json`; bump it there and the
build picks it up.

## Building locally instead (needs the Android SDK)

```bash
npm install
npm run android:init    # generates the android/ folder and applies native tweaks
npm run android:apk     # android/app/build/outputs/apk/debug/app-debug.apk
```

## What the native patches do

`patch-android.py` runs after the Android project is generated and:

- keeps the screen awake while the app is open, so it never sleeps mid-prayer
  and swallows touches
- adds the `VIBRATE` permission, so each counted touch gives a short buzz
- locks the app to portrait

## Keeping the screen on

In the APK this is settled natively by `FLAG_KEEP_SCREEN_ON`, and nothing can
override it. Opened as a plain web page the app has to fall back on two weaker
layers, both in `www/index.html`:

1. the Wake Lock API, which needs a secure context and so is missing on
   `file://`;
2. a muted 64×64 looping video, which Android will not sleep the screen during.

The video is why the page carries two small `data:video` blobs. Delete them and
the browser version will time out mid-prayer; the APK will not care.

## Files

```
www/index.html        the whole app
www/fonts/            Amiri + Tajawal, bundled so it works with no internet
assets/               source icon and splash art (1024px / 2732px)
make_icons.py         regenerates assets/ if you want to change the artwork
patch-android.py      native tweaks, applied after `cap add android`
capacitor.config.json app id and name
```
