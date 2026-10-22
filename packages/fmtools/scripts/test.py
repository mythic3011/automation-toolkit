import os
import moviepy.editor as mp
from moviepy.editor import vfx
from threading import Thread

# convert webm to gif


def convert_webm_to_gif(webm_path, gif_path):
    # 使用moviepy庫將webm轉換為gif
    video = mp.VideoFileClip(webm_path)
    video = video.fx(vfx.speedx, 2)  # Double the speed
    video.write_gif(gif_path)
    print('轉換完成: ' + gif_path)


def speed_up_gif(gif_path):
    # Open the gif
    clip = mp.VideoFileClip(gif_path)

    # Apply the speedx effect
    clip = clip.fx(vfx.speedx, 2)  # Double the speed

    # Write the result back to the file
    clip.write_gif(gif_path)


# 設定webm文件所在的目錄路徑
local_path = os.path.dirname(os.path.abspath(__file__))
webm_folder = local_path

# 設定gif文件的保存目錄路徑
gif_folder = local_path + '/gif'

# 遍歷webm目錄下的所有文件
threads = []
for filename in os.listdir(webm_folder):
    if filename.endswith('.webm'):
        # 構建webm文件的完整路徑
        webm_path = os.path.join(webm_folder, filename)

        # 構建相應gif文件的完整路徑
        gif_path = os.path.join(
            gif_folder, os.path.splitext(filename)[0] + '.gif')

        # Create a new thread for each conversion
        thread = Thread(target=convert_webm_to_gif, args=(webm_path, gif_path))
        threads.append(thread)
        thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
