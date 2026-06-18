"""
desktop_main.py — entry point for the self-contained CMAD.app build.

Starts the existing Flask app (app.py, unmodified in behavior — only its
resource paths were patched in app.py/paths.py) on a local loopback port,
then opens it in a native window via pywebview. Falls back to the system
default browser if pywebview isn't available for any reason.

This is the script PyInstaller should target (see cmad.spec), NOT app.py.
"""

import os
import shutil
import socket
import threading
import time
import webbrowser

from app import app, OUTPUT_FOLDER  # Flask app + writable output dir, both already path-patched


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def run_server(port):
    # Flask's built-in server is sufficient for a single local desktop user.
    # threaded=True lets app.py's gpu_lock queue concurrent jobs safely,
    # same as the gunicorn deployment does.
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True, use_reloader=False)


class Api:
    """
    Exposed to the webview's JS as `window.pywebview.api`. Works around
    WKWebView (macOS) not supporting Content-Disposition download prompts —
    instead of relying on the browser to handle the download, this opens a
    native "Save As" dialog and copies the already-generated file directly
    from OUTPUT_FOLDER to wherever the user picks.
    """

    def save_file(self, filename):
        import webview  # imported here so this module still loads if webview is absent

        # Guard against path traversal — only allow plain filenames we generated
        safe_name = os.path.basename(filename)
        src_path = os.path.join(OUTPUT_FOLDER, safe_name)

        if not os.path.isfile(src_path):
            return {"status": "error", "message": f"File not found: {safe_name}"}

        result = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG, save_filename=safe_name
        )
        if not result:
            return {"status": "cancelled"}

        dest_path = result if isinstance(result, str) else result[0]

        try:
            shutil.copyfile(src_path, dest_path)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return {"status": "ok", "path": dest_path}


def main():
    port = find_free_port()
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}/"
    time.sleep(1.0)  # give Flask a moment to bind before pointing a window at it

    try:
        import webview
        webview.create_window(
            "CMAD — Antarctic Sea Ice Anomaly Detector",
            url,
            width=1100,
            height=850,
            js_api=Api(),
        )
        webview.start()
    except Exception as e:
        print(f"[Desktop] Native window unavailable ({e}); opening default browser instead.")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
