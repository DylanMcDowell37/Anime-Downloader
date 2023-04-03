import os
import time
import tkinter
from tkinter import filedialog
import ffmpeg

def compress_video(video_full_path, output_file_name, target_size):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

root = tkinter.Tk()
root.withdraw() #use to hide tkinter window
anime = input('anime: ')

def search_for_file_path():
    currdir = os.getcwd()
    tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    if len(tempdir) > 0:
        print ("You chose: %s" % tempdir)
    return tempdir

def watch_for_new_files(dir_path):
    files = []
    while True:
        new_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        for file in new_files:
            if file.endswith('.ts') and file not in files:
                files.append(file)
                videoin = os.path.join(dir_path, file)
                videoout = os.path.join(dir_path, anime.replace(' ', '_')+file.replace('.ts', '.mp4'))
                compress_video(videoin, videoout, 50 * 1000)
                os.remove(videoin)
        time.sleep(10)

os.system('animdl download ' +'"'+ anime +'"')
file_path_variable = search_for_file_path()
print ("\nfile_path_variable = ", file_path_variable)

watch_for_new_files(file_path_variable)
