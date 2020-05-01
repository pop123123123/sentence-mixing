import youtube_dl, os, textgrid, config
from phonem_finding import get_best_phonem_combos
from sentence_to_phonems import get_phonems
from align import extract_subs, align_phonems
from phonem import Phonem
from serialize import save, load

# assuming french for now
def main(sentence, videos, skip=False):
  if skip:
    print('\n'*80)
    video_paths, phonems = load()
  # dl video sound and subtitles

  if not skip:
    video_paths = dl_videos(videos)

  # transcribe sentence to pseudo-phonetic string
  transcribed_sentence = get_phonems(sentence)[0]# Handle multiple sentences

  # saves all the subs chunks to the folder
  subs = []
  for audio_path, subs_path in video_paths:
    subs.extend(extract_subs(audio_path, subs_path))

  if not skip:
    # launches the program
    tmp_folder = align_phonems()

    # looks into the tmp_folder for text grids and phonems
    phonems = phonemes_from_subs(subs, tmp_folder)
    # save progress
    save(video_paths, phonems)

  # find the refined time location for each of the phonemes in the sound file
  available_combos = get_best_phonem_combos(transcribed_sentence, list(map(lambda x:x.get_phonem(), phonems)))

  # try sound mixing
  # evaluate
  # repeat to find optimum

  # return timestamps ranges for the parent function to mix them all
  import random
  available_combos = [[random.choice(combos)] for combos in available_combos]

  timestamps = []
  for combos in available_combos:
      for start, length in combos:
        timestamps.extend(phonems[start:start+length])
  return timestamps


def phonemes_from_subs(subs, tmp_folder):
  phonems = []
  for sub in subs:
    start_time = sub.get_start_timestamp()

    textgrid_path = os.path.join(tmp_folder, sub.get_basename_audio() + ".TextGrid")
    phonems.extend(parse_align_result(textgrid_path, start_time, sub.get_audio_path()))

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
      'writeautomaticsub': True,
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
  os.rmdir(config.get_property("folder"))

  # format: exe sentence url1 url2 ...
  if len(argv) >= 3:
    if argv[1] == 'skip':
      print(main(argv[2], argv[3:], skip=True))
    else:
      print(main(argv[1], argv[2:]))
