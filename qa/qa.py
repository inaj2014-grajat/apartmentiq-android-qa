"""Drive Chrome on the emulator from qa/steps.txt. Taps use uiautomator XML bounds only."""
import re, subprocess, sys, time, xml.etree.ElementTree as ET
from pathlib import Path

FRE = ["Use without an account", "Accept & continue", "No thanks", "No, thanks", "Got it", "Continue"]

def adb(*a, out=None):
    r = subprocess.run(["adb", *a], capture_output=True)
    if out:
        Path(out).write_bytes(r.stdout)
    return r.stdout.decode(errors="replace")

def dump(path):
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("exec-out", "cat", "/sdcard/ui.xml", out=path)
    try:
        return ET.parse(path).getroot()
    except Exception:
        return None

def find(root, text):
    if root is None:
        return None
    for n in root.iter("node"):
        if text in (n.get("text", "").strip(), n.get("content-desc", "").strip()):
            m = re.findall(r"\d+", n.get("bounds", ""))
            if len(m) == 4:
                x1, y1, x2, y2 = map(int, m)
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None

def clear_fre(out):
    for _ in range(4):
        root = dump(f"{out}/_fre.xml")
        hit = next((find(root, t) for t in FRE if find(root, t)), None)
        if not hit:
            return
        adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
        time.sleep(2)

def main(steps, out):
    n = 0
    for raw in Path(steps).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        op, _, arg = line.partition(" ")
        n += 1
        if op == "url":
            adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"'{arg}'", "com.android.chrome")
            time.sleep(5)
            clear_fre(out)
            print(f"[{n}] OPEN {arg}")
        elif op == "wait":
            time.sleep(float(arg))
        elif op == "back":
            adb("shell", "input", "keyevent", "4")
            print(f"[{n}] BACK")
        elif op == "shot":
            clear_fre(out)
            adb("exec-out", "screencap", "-p", out=f"{out}/{arg}.png")
            dump(f"{out}/{arg}.xml")
            print(f"[{n}] SHOT {arg}.png")
        elif op == "tap":
            clear_fre(out)
            root = dump(f"{out}/_tap{n}.xml")
            hit = find(root, arg)
            if hit:
                adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
                print(f"[{n}] TAP '{arg}' at {hit}")
            else:
                print(f"[{n}] MISSING '{arg}' (not in the UI tree)")
        else:
            print(f"[{n}] unknown step: {line}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
