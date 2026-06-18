from flask import Flask, render_template, request, send_from_directory
import os
import threading
import time
import uuid
from cmad_core import cmad_discord_for_two_images
from download_agent import download_and_crop_noaa_v4, check_internet_connection, NoaaConnectionError
from paths import get_base_path, get_app_data_dir

# Read-only bundled resources (templates, static, threshold files) — resolved
# relative to the PyInstaller bundle when frozen, or the script dir otherwise.
BASE_PATH = get_base_path()
LB_TXT_PATH = os.path.join(BASE_PATH, "lb15.txt")
Q1_TXT_PATH = os.path.join(BASE_PATH, "q115.txt")

# Writable runtime files — resolved to ~/Library/Application Support/CMAD when
# frozen (so the app never tries to write inside its own read-only bundle),
# or to the script dir otherwise (unchanged dev/gunicorn behavior).
DATA_DIR = get_app_data_dir()
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(DATA_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_PATH, "templates"),
    static_folder=os.path.join(BASE_PATH, "static"),
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# GPU lock — only one CMAD job runs at a time (MPS/GPU is not thread-safe)
# Other requests are queued and served as soon as the GPU is free
gpu_lock = threading.Lock()


# ── File helpers ──────────────────────────────────────────────────────────────

def delete_files(*file_paths):
    for fp in file_paths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                print(f"[Cleanup] Deleted: {fp}")
        except Exception as e:
            print(f"[Cleanup] Error: {e}")


def delayed_delete(*file_paths, delay=600):
    def _delete():
        time.sleep(delay)
        delete_files(*file_paths)
    threading.Thread(target=_delete, daemon=True).start()


def get_run_files(run_id):
    files = []
    if run_id and len(run_id) == 8 and run_id.isalnum():
        for folder in [OUTPUT_FOLDER, UPLOAD_FOLDER]:
            for f in os.listdir(folder):
                if run_id in f:
                    files.append(os.path.join(folder, f))
    return files


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    prev_run_id = request.args.get("cleanup", "")
    if prev_run_id:
        delete_files(*get_run_files(prev_run_id))
    return render_template("date_input.html")


from datetime import datetime

@app.route("/process", methods=["POST"])
def process_dates():
    date1 = request.form.get("date1")
    date2 = request.form.get("date2")
    error = None

    if not date1 or not date2:
        error = "Please enter both dates."

    if not error:
        try:
            d1 = datetime.strptime(date1, "%Y%m%d")
            d2 = datetime.strptime(date2, "%Y%m%d")
        except ValueError:
            error = "Dates must be in YYYYMMDD format."

    if not error and d1 >= d2:
        error = "Baseline date (t-n) must be earlier than target date (t)."

    if error:
        return render_template("date_input.html", error=error)

    # Check general internet connectivity FIRST — fails fast with a clear,
    # distinct message instead of being lumped in with "image not available
    # for that date" (which means something different: no internet at all).
    if not check_internet_connection():
        return render_template("date_input.html",
            error="No internet connection detected. Please check your network and try again.")

    run_id = uuid.uuid4().hex[:8]

    try:
        img1_path = download_and_crop_noaa_v4(date1, UPLOAD_FOLDER, suffix=run_id)
        img2_path = download_and_crop_noaa_v4(date2, UPLOAD_FOLDER, suffix=run_id)
    except NoaaConnectionError:
        # General internet is up (we just checked), but NOAA's server
        # specifically couldn't be reached — different from a 404/no-data case.
        return render_template("date_input.html",
            error="Could not reach NOAA's server right now. Please try again in a moment.")

    if img1_path is None or img2_path is None:
        return render_template("date_input.html",
            error="NOAA image not available for one or both dates.")

    output_filename = f"anomaly_{date2}_{date1}_{run_id}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Acquire GPU lock — if another user is running CMAD, this waits in queue
    # timeout=180s: if waiting more than 3 min, give up and show busy message
    acquired = gpu_lock.acquire(timeout=180)
    if not acquired:
        delete_files(img1_path, img2_path)
        return render_template("date_input.html",
            error="Server is busy — please try again in a moment.")

    try:
        cmad_discord_for_two_images(
            img1_path, img2_path,
            lb_txt_path=LB_TXT_PATH,
            q1_txt_path=Q1_TXT_PATH,
            show_plot=False,
            save_path=output_path
        )
    except Exception as e:
        delete_files(img1_path, img2_path, output_path)
        return render_template("date_input.html",
            error=f"Detection failed: {str(e)}")
    finally:
        gpu_lock.release()  # always release even if CMAD crashes

    delete_files(img1_path, img2_path)
    delayed_delete(output_path, delay=600)

    return render_template("result.html",
        image_file=output_filename,
        target_date=date2,
        run_id=run_id)


@app.route("/outputs/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    response = send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    delayed_delete(file_path, delay=30)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
