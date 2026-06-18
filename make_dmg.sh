#!/bin/bash
set -e

# make_dmg.sh — wraps dist/CMAD.app into a plain, shareable .dmg
# No Apple Developer Program membership or signing required.
#
# Run this AFTER build_mac_app.sh has produced dist/CMAD.app
#
# Usage:
#   chmod +x make_dmg.sh
#   ./make_dmg.sh

APP_NAME="CMAD"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}-Installer.dmg"
VOL_NAME="${APP_NAME} Installer"

if [ ! -d "$APP_PATH" ]; then
    echo "ERROR: $APP_PATH not found — run ./build_mac_app.sh first."
    exit 1
fi

echo "===================================="
echo "  Packaging $APP_PATH into $DMG_NAME"
echo "===================================="

rm -f "$DMG_NAME"
rm -rf dmg_staging
mkdir dmg_staging

cp -R "$APP_PATH" dmg_staging/
ln -s /Applications dmg_staging/Applications   # gives users the standard drag-to-Applications view

hdiutil create -volname "$VOL_NAME" -srcfolder dmg_staging -ov -format UDZO "$DMG_NAME"

rm -rf dmg_staging

echo ""
echo "========================================"
echo "  Done: $DMG_NAME"
echo ""
echo "  Share this file directly (email, Drive, USB, your"
echo "  own website, GitHub releases — anywhere). No Apple"
echo "  Developer account needed."
echo ""
echo "  Since it's unsigned, on first launch each user must:"
echo "    right-click CMAD.app -> Open -> Open"
echo "  (only required once per machine, after that it opens"
echo "  normally with a regular double-click)."
echo "========================================"
