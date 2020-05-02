from scipy.io import wavfile
import numpy as np

def concat_wav(path, segments):
  audio_files_dict = {}
  for phonem in segments:
    if not phonem.get_audio_path() in audio_files_dict:
      rate, data = wavfile.read(phonem.get_audio_path())

      if len(np.shape(data)) == 1 or data.shape[1] == 1:
        data = np.stack((data, data), axis=1)

      audio_files_dict[phonem.get_audio_path()] = (rate, data)


  new_clip = list(audio_files_dict.values())[0][1][:1]
  for segment in segments:
    rate, data = audio_files_dict[segment.get_audio_path()]

    start_frame = int(segment.get_start_timestamp()*rate)
    end_frame = int(segment.get_end_timestamp()*rate)

    new_clip = np.concatenate((new_clip, data[start_frame:end_frame]))

  wavfile.write(path, rate, new_clip)