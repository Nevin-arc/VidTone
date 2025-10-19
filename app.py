import os
from flask import Flask, request, render_template, redirect, url_for
import yt_dlp
from pathlib import Path

app = Flask(__name__)

DOWNLOADS = Path("downloads")

# Check if DOWNLOADS exists and is a directory; fix FileExistsError if it's a file
if not DOWNLOADS.is_dir():
    if DOWNLOADS.exists():
        DOWNLOADS.unlink()
    DOWNLOADS.mkdir(parents=True)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        fmt = request.form.get("format")
        playlist = request.form.get("playlist")
        folder = request.form.get("folder")

        if not folder:
            folder = "mobile_downloads"

        if not url:
            return "Please enter video URL", 400

        save_path = DOWNLOADS / folder
        save_path.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            'outtmpl': str(save_path / '%(title)s.%(ext)s'),
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
    # Read PORT env variable for Render deployment, default to 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
