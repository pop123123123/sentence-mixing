import youtube_dl, os, textgrid
from phonem_finding import get_best_phonem_combos
from sentence_to_phonems import get_phonems
from align import align_phonems
from phonem import Phonem

# assuming french for now
def main(sentence, videos):
  # dl video sound and subtitles

  video_paths = dl_videos(videos)

  # transcribe sentence to pseudo-phonetic string
  transcribed_sentence = get_phonems(sentence)[0]# Handle multiple sentences

  # transcribe all subtitles to phonetic

  # find all useful phonetics in subtitles, and match them to a range specific video location
  # save progress

  # find the refined time location for each of the phonemes in the sound file
  # save progress
  phonems = []
  for audio_path, subs_path in video_paths:
    phonems.extend(phonemes_from_subs(audio_path, subs_path))

  available_combos = get_best_phonem_combos(transcribed_sentence, list(map(lambda x:x.get_phonem(), phonems)))

  # try sound mixing
  # evaluate
  # repeat to find optimum

  # return timestamps ranges for the parent function to mix them all
  #print([(phonems[start][1][0], phonems[start + length - 1][1][1]) for combos in available_combos for start, length in combos])

def phonemes_from_subs(audio_path, subs_path):
  subs, folder = align_phonems(audio_path, subs_path)
  phonems = []
  for i, sub in enumerate(subs):
    start_time = sub.get_start_timestamp()
    phonems.extend(parse_align_result(f'{folder}/{i}.TextGrid', start_time, audio_path))
  return phonems

def parse_align_result(path, start_time, full_audio_path):
  if not os.path.exists(path):
    return []
  t = textgrid.TextGrid.fromFile(path)
  phones = t[1]

  return map(lambda x: Phonem(x.bounds()[0]+start_time, x.bounds()[1]+start_time, x.mark, full_audio_path), phones)

def dl_videos(urls):
  """
  Downloads audio and subs for videos at the given urls

  Arguments:
  - urls: iterable of youtube urls of the wanted videos

  Returns:
  A list of tuples (wave_file, subs_file) matching the given urls
  """
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
      base_path = os.path.splitext(filename)[0]
      paths.append((base_path + '.wav', base_path + '.fr.vtt'))# TODO handle dynamic extensions
  return paths

from sys import argv
if __name__ == "__main__":
  # format: exe sentence url1 url2 ...
  if len(argv) >= 3:
    main(argv[1], argv[2:])
