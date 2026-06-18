# CMAD — macOS Version

CMAD compares two NOAA/NSIDC Antarctic sea ice concentration images (one
baseline date, one target date) and highlights statistically anomalous
("discord") regions where the ice concentration changed in an unusual way
between the two dates. Developed as part of the **iHARP NSF HDR Institute**.

This repo builds CMAD as a self-contained, double-clickable macOS app —
no Python install required on the end user's machine.

The workflow: open the app, enter a baseline date and a target date
(`YYYYMMDD`), CMAD downloads both NOAA images, runs the anomaly detection,
and shows the result overlaid on the target-date image. You can save the
result image via a native Save dialog.

## Requirements

- **macOS.** Apple Silicon (M1/M2/M3/M4) gets GPU-accelerated detection via
  Metal (MPS); Intel Macs work too, automatically falling back to CPU —
  just slower. Detection is auto-selected at runtime, no configuration
  needed.
- An internet connection at runtime — CMAD downloads NOAA imagery live for
  whatever dates you enter; it doesn't work offline.

## Project structure

```
app.py                   Flask routes (date input, processing, results, download)
cmad_core.py              Core discord-anomaly detection (torch, auto MPS/CPU)
download_agent.py         NOAA image fetch + crop + connectivity checks
paths.py                  Resource/data path resolution (dev vs. packaged app)
desktop_main.py           Desktop entry point — runs Flask + native window
templates/                date_input.html, result.html
static/                   Logos, stylesheet
lb15.txt, q115.txt        Precomputed anomaly detection thresholds

cmad.spec                 PyInstaller build spec
requirements-desktop.txt  Build dependencies (PyInstaller, pywebview, etc.)
build_mac_app.sh          Builds dist/CMAD.app
make_dmg.sh               Packages CMAD.app into a shareable CMAD-Installer.dmg
check_device.py           Standalone MPS/CPU sanity check
```

## Building the app

```bash
chmod +x build_mac_app.sh make_dmg.sh
./build_mac_app.sh      # produces dist/CMAD.app
./make_dmg.sh           # produces CMAD-Installer.dmg
```

This must be run **on an actual Mac** — PyInstaller bundles whatever's
locally installed, including torch's Metal backend, which only exists on
real Apple hardware.

**Architecture matters**: the resulting app only runs on Macs of the same
architecture you built it on. Build on Apple Silicon → MPS-capable app,
Apple Silicon only. Build on Intel → CPU-only app, Intel only. To support
both, build once on each and offer two separate downloads.

No Apple Developer Program membership is required for this. The only
tradeoff: since the app isn't signed, each user has to right-click → Open →
Open the first time (standard macOS warning for unsigned apps from outside
the App Store). After that, it opens normally with a regular double-click.

Before building, sanity-check your Mac's device support:

```bash
python3 check_device.py
```

## Installing (for end users)

1. Download `CMAD-Installer.dmg` — you can download it directly from here:
   [CMAD macOS Installer (Google Drive)](https://drive.google.com/drive/folders/1KsU4wJbA3mRALOhNnesAkyFwNFKVzssQ?usp=sharing)
2. Open it, drag `CMAD.app` to Applications.
3. First launch: right-click `CMAD.app` → Open → Open (one-time, since
   the app is unsigned).
4. Enter two dates and run a detection.

## Known limitations

- Requires internet at runtime (NOAA image downloads).
- A build made on one Mac architecture won't open on the other.
- Without Apple Developer Program signing/notarization, first launch shows
  a one-time "unidentified developer" warning.

## Acknowledgments

Developed as part of the **iHARP NSF HDR Institute**, supported by the
National Science Foundation.

## License

© iHARP NSF HDR Institute — [https://iharp.umbc.edu/](https://iharp.umbc.edu/)

For licensing terms and usage permissions, please refer to iHARP or contact
the iHARP team directly.
