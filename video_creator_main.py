from video_creator.video import create_video_file
from video_creator.interface import loop_interface
from video_creator.download import dl_videos
from sys import argv

if __name__ == "__main__":
  # format: exe command (skip) sentence url1 url2 ...
  if len(argv) >= 3:
    command = argv[1]
    argv = argv[1:]

    skip = argv[1] == 'skip'
    if skip:
      argv = argv[1:]

    links = argv[1:]

    total_timestamps, total_text = loop_interface(command, skip, links)

    paths = dl_videos(links)
    create_video_file(total_timestamps, paths)
    print(total_text)
