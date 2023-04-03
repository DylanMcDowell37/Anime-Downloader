import os
import subprocess
import time

# Set the target size for the compressed video, in kilobits per second.
target_size = 50 * 1000

# Set the path to the directory where the downloaded files will be saved.
download_directory = "/path/to/download/directory"

# Set the path to the directory where the compressed files will be saved.
compress_directory = "/path/to/compress/directory"

# Define a function to compress a video file.
def compress_video(video_full_path, output_file_name):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration,bit_rate", "-of", "default=noprint_wrappers=1:nokey=1", video_full_path]).decode("utf-8")
    probe = probe.strip().split("\n")
    duration = float(probe[0])
    audio_bitrate = float(probe[1])

    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate

    video_bitrate = target_total_bitrate - audio_bitrate

    i = subprocess.Popen(["ffmpeg", "-i", video_full_path, "-c:v", "libx264", "-b:v", str(video_bitrate), "-pass", "1", "-f", "mp4", "-y", "/dev/null"], stderr=subprocess.PIPE)
    i.communicate()
    i = subprocess.Popen(["ffmpeg", "-i", video_full_path, "-c:v", "libx264", "-b:v", str(video_bitrate), "-pass", "2", "-c:a", "aac", "-b:a", str(audio_bitrate), "-y", output_file_name], stderr=subprocess.PIPE)
    i.communicate()

# Read the list of files from the text document.
with open("file_list.txt", "r") as f:
    file_list = f.readlines()

# Download each file in the list using wget.
for file_url in file_list:
    file_url = file_url.strip()
    file_name = file_url.split("/")[-1]
    download_path = os.path.join(download_directory, file_name)
    compress_path = os.path.join(compress_directory, file_name.replace(".ts", ".mp4"))

    # Download the file using wget.
    os.system("wget -O {} {}".format(download_path, file_url))

    # Compress the file using ffmpeg.
    compress_video(download_path, compress_path)

    # Remove the downloaded file.
    os.remove(download_path)

    # Wait for 1 second before processing the next file.
    time.sleep(1)

# Print a message indicating that all files have been processed.
print("All files have been processed.")
