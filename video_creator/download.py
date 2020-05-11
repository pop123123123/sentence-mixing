import os
import re

import youtube_dl


# workaround for youtube-dl issue #5710
class Logger(object):
    final_path = None

    def debug(self, msg):
        match = re.search(r"^\s*\[download\]\s(.*?)\shas.*$", msg)
        if match:
            self.final_path = match.group(1)

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def dl_video(url):
    log = Logger()
    ydl_opts = {
        "outtmpl": ".downloads/%(id)s.%(title)s.%(ext)s",
        "logger": log,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        filename = ydl.prepare_filename(ydl.extract_info(url))
        if not os.path.exists(filename):
            ydl.download([url])
        return log.final_path or filename
