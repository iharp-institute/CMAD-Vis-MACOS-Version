# CMAD — Antarctic Sea Ice Anomaly Detector

CMAD compares two NOAA/NSIDC Antarctic sea ice concentration images (one
baseline date, one target date) and highlights statistically anomalous
("discord") regions where the ice concentration changed in an unusual way
between the two dates. Developed as part of the **iHARP NSF HDR Institute**.

It ships two ways to run it:

- **Desktop Mac app** — a self-contained, double-clickable `.app` (no Python
  install required on the end user's machine). See [Building the Mac app](#building-the-mac-app)
  below.


Either way, the workflow is the same: enter a baseline date and a target
date (`YYYYMMDD`), CMAD downloads both NOAA images, runs the anomaly
detection, and shows the result overlaid on the target-date image.

## Requirements

- An internet connection at runtime — CMAD downloads NOAA imagery live for
  whatever dates you enter; it doesn't work offline.
- **macOS, Apple Silicon (M1/M2/M3/M4) recommended** for GPU-accelerated
  detection via Metal (MPS). Intel Macs work too, falling back to CPU
  automatically — just slower.

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

cmad.spec                 PyInstaller build spec for the Mac desktop app
requirements-desktop.txt  Deps for building the desktop app
build_mac_app.sh          Builds dist/CMAD.app
make_dmg.sh               Packages CMAD.app into a shareable CMAD-Installer.dmg
check_device.py           Standalone MPS/CPU sanity check


```

## Building the Mac app

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
both, build once on each and offer two downloads.

No Apple Developer Program membership is required for this. The only
tradeoff: since the app isn't signed, each user has to right-click → Open →
Open the first time (standard macOS warning for unsigned apps from outside
the App Store). After that, it opens normally with a regular double-click.

Before building, sanity-check your Mac's device support:

```bash
python3 check_device.py
```

## Running from source (development)

```bash
pip install -r requirements.txt
python3 app.py
```

Then open `http://localhost:5000`.



## Known limitations

- Requires internet at runtime (NOAA image downloads).
- A `.dmg` built on one Mac architecture won't open on the other.
- Without Apple Developer Program signing/notarization, first launch shows
  a one-time "unidentified developer" warning.

## Acknowledgments

Developed as part of the **iHARP NSF HDR Institute**, supported by the
National Science Foundation.

## License

*(Add a license of your choice here — e.g. MIT, BSD-3-Clause, or your
institution's preferred license. None is currently specified.)*
# CMAD-Vis-MACOS-Version
