"""
Ad-hoc developer scratch script.

NOTE: Despite the filename, this is **not** a pytest test module. It is a
one-off helper that converts every ``*.webm`` file in the script's own
directory into a 2x-speed GIF placed under a sibling ``gif/`` folder, using
threads. It is kept here for historical convenience only — prefer
``convert_media.py`` for batch conversions.

Importing this module is safe; the conversion runs only when executed
directly (``python test.py``).
"""

import os
import moviepy.editor as mp
from moviepy.editor import vfx
from threading import Thread


def convert_webm_to_gif(webm_path, gif_path):
    # Convert webm to gif with moviepy at 2x speed.
    video = mp.VideoFileClip(webm_path)
    try:
        sped = video.fx(vfx.speedx, 2)
        try:
            sped.write_gif(gif_path)
        finally:
            sped.close()
    finally:
        video.close()
    print('Converted: ' + gif_path)


def speed_up_gif(gif_path):
    """Double the playback speed of a GIF in place."""
    # moviepy cannot safely overwrite the GIF it is reading; write next to
    # it and then replace.
    tmp_path = gif_path + ".speed_tmp.gif"
    clip = mp.VideoFileClip(gif_path)
    try:
        sped = clip.fx(vfx.speedx, 2)
        try:
            sped.write_gif(tmp_path)
        finally:
            sped.close()
    finally:
        clip.close()
    os.replace(tmp_path, gif_path)


def main():
    # Locate files relative to this script so the helper works regardless
    # of the invoking directory.
    local_path = os.path.dirname(os.path.abspath(__file__))
    webm_folder = local_path
    gif_folder = os.path.join(local_path, 'gif')
    os.makedirs(gif_folder, exist_ok=True)

    threads = []
    for filename in os.listdir(webm_folder):
        if not filename.lower().endswith('.webm'):
            continue
        webm_path = os.path.join(webm_folder, filename)
        gif_path = os.path.join(
            gif_folder, os.path.splitext(filename)[0] + '.gif')

        thread = Thread(target=convert_webm_to_gif, args=(webm_path, gif_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
