import youtube_dl, os

# assuming french for now
def main(sentence, videos):
  # dl video sound and subtitles

  dl_videos(videos)

  # transcribe sentence to pseudo-phonetic string

  # transcribe all subtitles to phonetic

  # find all useful phonetics in subtitles, and match them to a range specific video location
  # save progress

  # find the refined time location for each of the phonemes in the sound file
  # save progress

  # try sound mixing
  # evaluate
  # repeat to find optimum

  # return timestamps ranges for the parent function to mix them all

def dl_videos(urls):
  paths = []
  for url in urls:
    ydl_opts = {
      'writesubtitles': True,
      'subtitleslangs': [
        'fr',
      ],
      'outtmpl': 'downloads/%(title)s.%(ext)s',
      'format': 'bestaudio/best',
      'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
      }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      filename = ydl.prepare_filename(ydl.extract_info(url))
      ydl.download([url])
      paths.append(os.path.splitext(filename)[0])# TODO handle subs + audio
  return paths

from sys import argv
if __name__ == "__main__":
  # format: exe sentence url1 url2 ...
  if len(argv) >= 3:
    main(argv[1], argv[2:])