# assuming french for now
def main(sentence, videos):
  # dl video sound and subtitles
  
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

import sys
if __name__ == "__main__":
  # format: exe sentence url1 url2 ...
  if len(sys.argv) >= 3:
    main(argv[1], argv[2:])