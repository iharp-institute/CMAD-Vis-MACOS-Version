#!/bin/bash
set -e

echo "===================================="
echo "  Building CMAD.app (self-contained, macOS)"
echo "===================================="

ARCH=$(uname -m)
echo "Building on architecture: $ARCH"
echo "(the resulting app will only run on $ARCH Macs)"
echo ""

python3 -m venv build_env
source build_env/bin/activate

pip install --upgrade pip
pip install -r requirements-desktop.txt

rm -rf build dist

pyinstaller cmad.spec --noconfirm

deactivate

if [ -d "dist/CMAD.app" ]; then
    echo ""
    echo "========================================"
    echo "  Build complete: dist/CMAD.app"
    echo "  Architecture: $ARCH"
    echo ""
    echo "  First launch will likely trigger a Gatekeeper"
    echo "  warning since this isn't notarized. Either:"
    echo "    - right-click CMAD.app -> Open -> Open, or"
    echo "    - run: xattr -cr dist/CMAD.app  (strips quarantine flag)"
    echo "========================================"
else
    echo "ERROR: build failed — check the PyInstaller output above."
    exit 1
fi
