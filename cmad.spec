# cmad.spec
#
# Build with:  pyinstaller cmad.spec --noconfirm
# (or just run ./build_mac_app.sh, which does this for you)
#
# Must be run ON a Mac, inside a venv where requirements-desktop.txt has been
# installed. The resulting CMAD.app will only run on Macs of the SAME
# architecture as the machine you build on (arm64 Apple Silicon -> MPS-capable
# app limited to Apple Silicon; x86_64 Intel -> CPU-only app limited to Intel).

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# torch, opencv, and matplotlib all ship native binaries / data files that
# PyInstaller doesn't pick up automatically — collect_all grabs everything.
for pkg in ("torch", "cv2", "matplotlib", "flask"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Bundled READ-ONLY resources the app needs at runtime.
# NOTE: this assumes a "templates/" folder (date_input.html, result.html) and
# a "static/" folder (nsf-logo.png, iharp-logo.jpg, etc.) sit next to app.py
# in your project — adjust these paths if your layout differs.
datas += [
    ("templates", "templates"),
    ("static", "static"),
    ("lb15.txt", "."),
    ("q115.txt", "."),
]

a = Analysis(
    ["desktop_main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CMAD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # GUI app — no terminal window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="CMAD",
)

app = BUNDLE(
    coll,
    name="CMAD.app",
    icon=None,  # put a path to a .icns file here if you have an app icon
    bundle_identifier="edu.iharp.cmad",
    info_plist={
        "NSHighResolutionCapable": "True",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "iHARP / NSF HDR Institute",
    },
)
