import youtube_dl, os

def dl_videos(urls):
  paths = []
  for url in urls:
    ydl_opts = {
      'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      filename = ydl.prepare_filename(ydl.extract_info(url))
      if not os.path.exists(filename):
        ydl.download([url])
      paths.append(filename)
  return paths