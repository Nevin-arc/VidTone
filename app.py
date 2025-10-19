import os
import shutil
from flask import Flask, request, render_template, redirect, url_for
import yt_dlp
from pathlib import Path

app = Flask(__name__)

# Setup downloads folder safely
DOWNLOADS = Path("downloads")
if not DOWNLOADS.is_dir():
    if DOWNLOADS.exists():
        DOWNLOADS.unlink()
    DOWNLOADS.mkdir(parents=True)

# Secret file paths for cookies
SECRET_COOKIES_PATH = Path('/etc/secrets/cookies.txt')  # Render secret file (read-only)
LOCAL_COOKIES_PATH = Path('cookies.txt')  # Writable local copy

# Copy secret cookies to writable location on app start
if SECRET_COOKIES_PATH.exists() and not LOCAL_COOKIES_PATH.exists():
    shutil.copy(SECRET_COOKIES_PATH, LOCAL_COOKIES_PATH)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        fmt = request.form.get("format")
        playlist = request.form.get("playlist")
        folder = request.form.get("folder") or "mobile_downloads"

        if not url:
            return "Please enter video URL", 400

        save_path = DOWNLOADS / folder
        save_path.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            'outtmpl': str(save_path / '%(title)s.%(ext)s'),
            'cookiefile': str(LOCAL_COOKIES_PATH),
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
                )
            },
            'quiet': True,
            'no_warnings': True,
        }

        if fmt == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })

        if playlist == "no":
            ydl_opts['noplaylist'] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            return f"Download failed: {e}", 500

        return redirect(url_for('index'))

    return render_template("index.html")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
