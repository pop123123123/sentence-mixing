from main import main
import youtube_dl, os
from moviepy.editor import VideoFileClip, concatenate_videoclips

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

from sys import argv
if __name__ == "__main__":
  # format: exe (skip) sentence url1 url2 ...
  if len(argv) >= 3:
    if argv[1] == 'skip':
      timestamps = main(argv[2], argv[3:], skip=True)
      argv = argv[1:]
    else:
      timestamps = main(argv[1], argv[2:])

    paths = dl_videos(argv[2:])
    clip = VideoFileClip(paths[0])
    clips = [clip.subclip(*seg) for seg in timestamps]
    concatenate_videoclips(clips).write_videofile("out.mp4")
