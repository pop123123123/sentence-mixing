import youtube_dl, os

def dl_video(url):
  ydl_opts = {
    'outtmpl': 'downloads/%(title)s.%(ext)s',
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    filename = ydl.prepare_filename(ydl.extract_info(url))
    if not os.path.exists(filename):
      ydl.download([url])
    return filename