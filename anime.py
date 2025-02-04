import os
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
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

def search_for_file_path():
    # Get the list of directories in the current working directory
    dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    # Sort the directories by creation time (newest first)
    dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
    # Return the newest directory
    if dirs:
        return os.path.abspath(dirs[0])

anime = input('anime: ')
file_path_variable = search_for_file_path()
if file_path_variable:
    print("Newest directory: ", file_path_variable)
    for files in os.listdir(file_path_variable):
        videoin = os.path.join(file_path_variable, files)
        videoout = os.path.join(file_path_variable, "compressed" + files.replace('.ts', '.mp4'))
        compress_video(videoin, videoout, 50 * 1000)
        os.remove(videoin)
else:
    print("No directories found.")


