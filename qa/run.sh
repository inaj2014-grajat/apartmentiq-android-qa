#!/usr/bin/env bash
# Runs on the GitHub runner with the emulator up. Never stops on one failed step.
set -u
OUT=out; mkdir -p "$OUT"
adb wait-for-device
adb shell getprop ro.build.version.release > "$OUT/android-version.txt"
adb shell wm size > "$OUT/screen-size.txt"
# Chrome without the first-run screens.
adb shell 'echo "_ --disable-fre --no-default-browser-check --no-first-run" > /data/local/tmp/chrome-command-line'
adb shell am set-debug-app --persistent com.android.chrome || true
adb shell pm list packages | grep -i chrome > "$OUT/chrome-package.txt" || echo "NO CHROME" > "$OUT/chrome-package.txt"
adb logcat -c
python3 qa/qa.py qa/steps.txt "$OUT" 2>&1 | tee "$OUT/steps.log"
adb logcat -d -s chromium:V cr_*:V AndroidRuntime:E > "$OUT/logcat-chrome.txt" || true
adb logcat -b crash -d > "$OUT/crash.txt" || true
exit 0
