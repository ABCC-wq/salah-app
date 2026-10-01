#!/usr/bin/env python3
"""
Runs after `npx cap add android`. Applies the three native tweaks the web layer
can't do on its own, then leaves the rest of the generated project untouched.

  1. screen stays awake while the app is open (a sleeping screen eats touches)
  2. VIBRATE permission, so navigator.vibrate() confirms each count
  3. portrait lock
"""
import pathlib, re, sys

root = pathlib.Path("android/app/src/main")

# ---- 1. MainActivity: keep the screen on -----------------------------------
act = next(root.glob("java/**/MainActivity.java"), None)
if act is None:
    sys.exit("MainActivity.java not found — did `npx cap add android` run?")

pkg = re.search(r"^package\s+([\w.]+);", act.read_text(), re.M).group(1)
act.write_text(f"""package {pkg};

import android.os.Bundle;
import android.view.WindowManager;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {{
    @Override
    public void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }}
}}
""")
print(f"patched MainActivity ({pkg})")

# ---- 2 & 3. Manifest: vibrate permission + portrait lock -------------------
mf = root / "AndroidManifest.xml"
xml = mf.read_text()

if "android.permission.VIBRATE" not in xml:
    xml = xml.replace(
        "    <application",
        '    <uses-permission android:name="android.permission.VIBRATE" />\n\n    <application',
        1,
    )
    print("added VIBRATE permission")

if "android:screenOrientation" not in xml:
    xml, n = re.subn(
        r'(<activity\b[^>]*?android:name="\.MainActivity")',
        r'\1\n            android:screenOrientation="portrait"',
        xml,
        count=1,
    )
    if n == 0:
        sys.exit("could not find the MainActivity <activity> tag to lock orientation")
    print("locked orientation to portrait")

mf.write_text(xml)
print("manifest patched")

# ---- 4. Version name, taken from package.json ------------------------------
import json

version = json.loads(pathlib.Path("package.json").read_text())["version"]
bg = pathlib.Path("android/app/build.gradle")
gradle, n = re.subn(r'versionName\s+"[^"]*"', f'versionName "{version}"', bg.read_text(), count=1)
if n:
    bg.write_text(gradle)
    print(f"versionName set to {version}")
