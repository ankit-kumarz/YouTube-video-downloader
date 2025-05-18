from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify
import yt_dlp
import os
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_video_info(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('Please enter a YouTube URL.', 'danger')
            return redirect(url_for('index'))
        try:
            info = get_video_info(url)
            formats = []
            for f in info['formats']:
                if f.get('format_id') and f.get('ext'):
                    label = ''
                    if f.get('vcodec') == 'none':
                        label = 'Audio only'
                    elif f.get('acodec') == 'none':
                        label = 'Video only'
                    else:
                        label = 'Video+Audio'
                    f['label'] = label
                    formats.append(f)
            return render_template('index.html', info=info, formats=formats, url=url)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('index'))
    return render_template('index.html', info=None)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    if not url or not format_id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('index'))
    ydl_opts = {
        'format': format_id,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True) 
